"""Analysis service wrapping existing MedBillDozer orchestrator."""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path for importing medbilldozer modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.services.db_service import get_db_service
from app.services.storage_service import get_storage_service
from app.utils import get_logger, log_with_context

from medbilldozer.core.document_identity import maybe_enhance_identity
from medbilldozer.core.transaction_normalization import (
    deduplicate_transactions,
    normalize_line_items,
)

logger = get_logger(__name__)


class AnalysisService:
    """
    Wraps existing OrchestratorAgent for async analysis execution.
    Integrates with GCS for document retrieval and Supabase for persistence.
    """

    def __init__(self):
        """Initialize analysis service."""
        logger.info("🔧 Initializing AnalysisService...")
        self.storage = get_storage_service()
        logger.info("  ✓ StorageService initialized")
        self.db = get_db_service()
        logger.info("  ✓ DBService initialized")
        from app.services.multimodal_analysis_service import MultimodalAnalysisService

        logger.info("  ⏳ Initializing MultimodalAnalysisService...")
        self.multimodal_service = MultimodalAnalysisService()
        logger.info("  ✓ MultimodalAnalysisService initialized")
        logger.info("✅ AnalysisService ready")

    async def run_analysis(
        self,
        analysis_id: str,
        document_ids: List[str],
        user_id: str,
        provider: str = "medgemma-ensemble",
    ) -> Dict[str, Any]:
        """
        Run MedGemma analysis on uploaded documents (background task).

        Args:
            analysis_id: Unique analysis ID
            document_ids: List of document IDs to analyze
            user_id: User ID
            provider: AI provider to use (default: medgemma-ensemble)

        Returns:
            Analysis results dict
        """
        try:
            log_with_context(
                logger,
                20,
                "🚀 Starting analysis workflow",
                analysis_id=analysis_id,
                user_id=user_id,
                document_count=len(document_ids),
                provider=provider,
            )

            # Update status to processing
            await self.db.update_analysis_status(analysis_id, "processing")
            log_with_context(
                logger,
                20,
                "📝 Updated analysis status to 'processing'",
                analysis_id=analysis_id,
                user_id=user_id,
            )

            # Check if any documents are images (multimodal analysis needed)
            has_images = await self._check_for_images(document_ids, user_id)
            log_with_context(
                logger,
                20,
                f"🔍 Checked for images: {has_images}",
                analysis_id=analysis_id,
                user_id=user_id,
                has_images=has_images,
            )

            # Use multimodal service if images are present
            if has_images:
                logger.info(f"📷 Using multimodal analysis for analysis {analysis_id}")
                return await self._run_multimodal_analysis(
                    analysis_id, document_ids, user_id, provider
                )

            # Otherwise, continue with text-only analysis
            # Import existing medbilldozer modules
            from medbilldozer.core.coverage_matrix import build_coverage_matrix
            from medbilldozer.core.orchestrator_agent import OrchestratorAgent
            from medbilldozer.providers.provider_registry import (
                ProviderRegistry,
                register_providers,
            )

            # Ensure providers are registered
            register_providers()

            # Wire medgemma-ensemble inner provider:
            #   - HF_ENDPOINT_BASE set → use MedGemmaHostedProvider (dedicated endpoint)
            #   - otherwise           → use gpt-4o-mini (HF serverless returns 400 for gated models)
            import os

            try:
                from medbilldozer.providers.medgemma_ensemble_provider import (
                    MedGemmaEnsembleProvider,
                )

                ensemble = MedGemmaEnsembleProvider.__new__(MedGemmaEnsembleProvider)
                ensemble.enable_openai = False
                if os.getenv("HF_ENDPOINT_BASE"):
                    from medbilldozer.providers.medgemma_hosted_provider import (
                        MedGemmaHostedProvider,
                    )

                    ensemble.medgemma = MedGemmaHostedProvider()
                    inner = "MedGemma (dedicated endpoint)"
                else:
                    from medbilldozer.providers.openai_analysis_provider import (
                        OpenAIAnalysisProvider,
                    )

                    ensemble.medgemma = OpenAIAnalysisProvider("gpt-4o-mini")
                    inner = "gpt-4o-mini (fallback)"
                ProviderRegistry.register("medgemma-ensemble", ensemble)
                log_with_context(
                    logger,
                    20,
                    f"✅ Registered medgemma-ensemble with {inner}",
                    analysis_id=analysis_id,
                )
            except Exception as reg_err:
                log_with_context(
                    logger,
                    30,
                    f"⚠️  medgemma-ensemble registration failed: {str(reg_err)}",
                    analysis_id=analysis_id,
                )

            if provider not in ProviderRegistry.list():
                log_with_context(
                    logger,
                    30,
                    f"⚠️  Provider '{provider}' not registered, falling back to 'medgemma-ensemble'",
                    analysis_id=analysis_id,
                    user_id=user_id,
                    requested_provider=provider,
                )
                provider = "medgemma-ensemble"  # Fallback to ensemble

            logger.info(f"📚 Downloading {len(document_ids)} document(s) from storage...")

            # Download documents from GCS and prepare for analysis
            documents = []
            for doc_id in document_ids:
                doc_meta = await self.db.get_document(doc_id, user_id)
                if not doc_meta:
                    log_with_context(
                        logger,
                        30,
                        "⚠️  Document not found in database",
                        analysis_id=analysis_id,
                        user_id=user_id,
                        document_id=doc_id,
                    )
                    continue

                # Download raw text from GCS
                try:
                    raw_text = await self.storage.download_text(
                        bucket_name=self.storage.documents_bucket, blob_path=doc_meta["gcs_path"]
                    )
                    log_with_context(
                        logger,
                        20,
                        "✅ Downloaded document from GCS",
                        analysis_id=analysis_id,
                        document_id=doc_id,
                        filename=doc_meta["filename"],
                    )
                except Exception as e:
                    # If download fails, use extracted_text from metadata
                    log_with_context(
                        logger,
                        30,
                        "⚠️  GCS download failed, using extracted_text fallback",
                        analysis_id=analysis_id,
                        document_id=doc_id,
                        error=str(e),
                    )
                    raw_text = doc_meta.get("extracted_text") or ""

                # Ensure raw_text is never None - if missing, extract on-demand
                if not raw_text or not isinstance(raw_text, str):
                    log_with_context(
                        logger,
                        30,
                        "⚠️  No extracted text found, attempting on-demand extraction",
                        analysis_id=analysis_id,
                        document_id=doc_id,
                    )

                    content_type = doc_meta.get("content_type", "")

                    # For plain-text files, download bytes and decode directly
                    # (avoids erroneously running PyPDF2 on .txt content)
                    if "text" in content_type:
                        try:
                            raw_bytes = await self.storage.download_bytes(
                                bucket_name=self.storage.documents_bucket,
                                blob_path=doc_meta["gcs_path"],
                            )
                            raw_text = raw_bytes.decode("utf-8", errors="replace")
                            log_with_context(
                                logger,
                                20,
                                f"✅ Decoded text file directly ({len(raw_text)} chars)",
                                analysis_id=analysis_id,
                                document_id=doc_id,
                            )
                        except Exception as txt_error:
                            log_with_context(
                                logger,
                                40,
                                f"❌ Text file decode failed: {str(txt_error)}",
                                analysis_id=analysis_id,
                                document_id=doc_id,
                                error=str(txt_error),
                            )
                            continue  # Skip this document
                    else:
                        # For binary formats (PDF, etc.), extract with PyPDF2
                        try:
                            raw_text = await self._extract_text_from_pdf(
                                doc_meta["gcs_path"], doc_id
                            )

                            if raw_text:
                                log_with_context(
                                    logger,
                                    20,
                                    f"✅ Extracted text on-demand ({len(raw_text)} chars)",
                                    analysis_id=analysis_id,
                                    document_id=doc_id,
                                )
                            else:
                                log_with_context(
                                    logger,
                                    40,
                                    "❌ On-demand extraction failed - no text extracted",
                                    analysis_id=analysis_id,
                                    document_id=doc_id,
                                )
                                continue  # Skip this document
                        except Exception as extract_error:
                            log_with_context(
                                logger,
                                40,
                                f"❌ On-demand text extraction failed: {str(extract_error)}",
                                analysis_id=analysis_id,
                                document_id=doc_id,
                                error=str(extract_error),
                            )
                            continue  # Skip this document

                # Cache extracted text to database so it can be displayed in the UI
                try:
                    await self.db.update_document_extracted_text(
                        document_id=doc_id,
                        extracted_text=raw_text,
                    )
                    log_with_context(
                        logger,
                        20,
                        f"💾 Cached extracted text ({len(raw_text)} chars)",
                        analysis_id=analysis_id,
                        document_id=doc_id,
                    )
                except Exception as cache_err:
                    log_with_context(
                        logger,
                        30,
                        f"⚠️  Failed to cache extracted text: {str(cache_err)}",
                        analysis_id=analysis_id,
                        document_id=doc_id,
                    )

                documents.append(
                    {
                        "document_id": doc_id,
                        "raw_text": raw_text,
                        "filename": doc_meta["filename"],
                        "document_type": doc_meta.get("document_type"),
                        "facts": {},
                    }
                )

            if not documents:
                log_with_context(
                    logger,
                    40,
                    "❌ No documents could be loaded for analysis",
                    analysis_id=analysis_id,
                    user_id=user_id,
                )
                await self.db.update_analysis_status(
                    analysis_id, "failed", error_message="No documents found"
                )
                return {"status": "failed", "error": "No documents found"}

            log_with_context(
                logger,
                20,
                f"📄 Prepared {len(documents)} document(s) for analysis",
                analysis_id=analysis_id,
                user_id=user_id,
                document_count=len(documents),
            )

            # Run orchestrator for each document (REUSE EXISTING CODE)
            results = []
            log_with_context(
                logger,
                20,
                f"🔄 Starting document loop with {len(documents)} documents",
                analysis_id=analysis_id,
                document_keys=str(
                    [list(d.keys()) for d in documents[:2]]
                ),  # Show keys of first 2 docs
            )
            for idx, doc in enumerate(documents, 1):
                log_with_context(
                    logger,
                    20,
                    f"📋 Processing document {idx}, type: {type(doc)}, keys: {list(doc.keys()) if isinstance(doc, dict) else 'NOT A DICT'}",
                    analysis_id=analysis_id,
                )
                doc_id = doc["document_id"]
                doc_started_at = datetime.utcnow().isoformat()

                log_with_context(
                    logger,
                    20,
                    f"🔬 Analyzing document {idx}/{len(documents)}",
                    analysis_id=analysis_id,
                    document_id=doc_id,
                    document_filename=doc["filename"],
                    provider=provider,
                )

                try:
                    orchestrator = OrchestratorAgent(
                        analyzer_override=provider,
                        profile_context=None,  # TODO: load user profile from DB
                    )

                    # Create progress callback that updates database
                    def progress_callback(workflow_log, step_status):
                        """Update database with current phase."""
                        try:
                            log_with_context(
                                logger,
                                20,
                                f"📊 Analysis progress: {step_status}",
                                analysis_id=analysis_id,
                                document_id=doc_id,
                                phase=step_status,
                            )
                            # Use asyncio to call async method from sync callback
                            import asyncio

                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(
                                self.db.update_document_progress(
                                    analysis_id=analysis_id,
                                    document_id=doc_id,
                                    phase=step_status,
                                    started_at=doc_started_at,
                                    workflow_log=workflow_log,
                                )
                            )
                            loop.close()
                        except Exception as e:
                            log_with_context(
                                logger,
                                30,
                                "⚠️  Progress update failed",
                                analysis_id=analysis_id,
                                document_id=doc_id,
                                error=str(e),
                            )

                    # Initialize progress as "starting"
                    await self.db.update_document_progress(
                        analysis_id=analysis_id,
                        document_id=doc_id,
                        phase="pre_extraction_active",
                        started_at=doc_started_at,
                    )

                    # Run analysis with progress callback
                    try:
                        result = orchestrator.run(
                            doc["raw_text"], progress_callback=progress_callback
                        )
                    except KeyError as ke:
                        logger.error(f"KeyError during orchestrator.run(): {ke}")
                        logger.exception("Full traceback:")
                        raise
                    except Exception as e:
                        logger.error(f"Error during orchestrator.run(): {type(e).__name__}: {e}")
                        raise

                    # Validate result structure
                    if not isinstance(result, dict):
                        raise ValueError(f"Orchestrator returned non-dict result: {type(result)}")

                    # Mark as complete
                    await self.db.update_document_progress(
                        analysis_id=analysis_id,
                        document_id=doc_id,
                        phase="complete",
                        started_at=doc_started_at,
                    )

                    log_with_context(
                        logger,
                        20,
                        "✅ Document analysis completed successfully",
                        analysis_id=analysis_id,
                        document_id=doc_id,
                        document_filename=doc["filename"],
                        result_keys=(
                            list(result.keys()) if isinstance(result, dict) else "not-a-dict"
                        ),
                    )

                    # Convert AnalysisResult dataclass to a plain dict for JSON serialization.
                    # The orchestrator returns an AnalysisResult object, not a dict;
                    # dict-style access ("issues" in analysis_obj) raises TypeError otherwise.
                    raw_analysis = result.get("analysis")
                    analysis_dict = self._serialize_analysis(raw_analysis)

                    # Build document result with facts and analysis
                    doc_result = {
                        "document_id": doc_id,
                        "filename": doc["filename"],
                        "facts": result.get("facts", {}),
                        "analysis": analysis_dict,
                        "orchestration": result.get("_orchestration", {}),
                        "progress": {
                            "phase": "complete",
                            "started_at": doc_started_at,
                            "completed_at": datetime.utcnow().isoformat(),
                        },
                    }

                    # Enhance document with identity fingerprint (same as Streamlit app)
                    # This adds canonical fingerprint and friendly document ID
                    try:
                        maybe_enhance_identity(doc_result)
                        log_with_context(
                            logger,
                            20,
                            "✅ Document identity enhanced",
                            analysis_id=analysis_id,
                            document_id=doc_id,
                            friendly_id=doc_result.get("document_id"),
                            fingerprint=doc_result.get("internal_id"),
                        )
                    except Exception as e:
                        log_with_context(
                            logger,
                            30,
                            f"⚠️  Document identity enhancement failed: {str(e)}",
                            analysis_id=analysis_id,
                            document_id=doc_id,
                        )

                    results.append(doc_result)
                except Exception as e:
                    log_with_context(
                        logger,
                        40,
                        f"❌ Document analysis failed: {type(e).__name__}",
                        analysis_id=analysis_id,
                        document_id=doc_id,
                        document_filename=doc["filename"],
                        error=str(e),
                    )
                    logger.exception(f"Document {doc_id} analysis failed")

                    # Mark as failed
                    await self.db.update_document_progress(
                        analysis_id=analysis_id,
                        document_id=doc_id,
                        phase="failed",
                        started_at=doc_started_at,
                    )

                    results.append(
                        {
                            "document_id": doc_id,
                            "filename": doc["filename"],
                            "error": str(e),
                            "status": "failed",
                            "progress": {
                                "phase": "failed",
                                "started_at": doc_started_at,
                                "failed_at": datetime.utcnow().isoformat(),
                                "error_message": str(e),
                            },
                        }
                    )

            # Transaction normalization (cross-document, same as Streamlit)
            all_normalized_transactions = []
            transaction_provenance = {}
            try:
                log_with_context(
                    logger,
                    20,
                    f"💳 Normalizing transactions across {len(results)} documents",
                    analysis_id=analysis_id,
                )

                for doc_result in results:
                    if "error" in doc_result:
                        continue  # Skip failed documents

                    # Extract line items from facts
                    line_items = doc_result.get("facts", {}).get("line_items", [])
                    if not line_items:
                        log_with_context(
                            logger,
                            30,
                            "⚠️  No line items found in document",
                            analysis_id=analysis_id,
                            document_id=doc_result.get("document_id"),
                        )
                        continue

                    # Normalize line items
                    normalized = normalize_line_items(
                        line_items=line_items,
                        source_document_id=doc_result.get("document_id", ""),
                    )
                    all_normalized_transactions.extend(normalized)

                # Cross-document deduplication
                if all_normalized_transactions:
                    unique_transactions, transaction_provenance = deduplicate_transactions(
                        all_normalized_transactions
                    )
                    log_with_context(
                        logger,
                        20,
                        "✅ Transaction deduplication complete",
                        analysis_id=analysis_id,
                        total_transactions=len(all_normalized_transactions),
                        unique_transactions=len(unique_transactions),
                    )

                    # Convert to dict for JSON serialization
                    normalized_transactions_list = [
                        tx.__dict__ for tx in unique_transactions.values()
                    ]
                else:
                    normalized_transactions_list = []

            except Exception as e:
                log_with_context(
                    logger,
                    30,
                    "⚠️  Transaction normalization failed",
                    analysis_id=analysis_id,
                    error=str(e),
                )
                normalized_transactions_list = []
                transaction_provenance = {}

            # Build coverage matrix (REUSE EXISTING CODE)
            coverage_matrix = None
            try:
                if len(results) > 1:
                    logger.info(f"🔗 Building coverage matrix for {len(results)} documents...")
                    coverage_matrix = build_coverage_matrix(results)
                    # Ensure it's a dict or None — build_coverage_matrix may return []
                    if not isinstance(coverage_matrix, dict):
                        coverage_matrix = None
                    logger.info("✅ Coverage matrix built successfully")
            except Exception as e:
                log_with_context(
                    logger,
                    30,
                    "⚠️  Coverage matrix build failed",
                    analysis_id=analysis_id,
                    error=str(e),
                )

            # Calculate total savings and issue count
            # Note: result["analysis"] is now a plain dict (serialized from AnalysisResult)
            total_savings = 0
            all_issues = []
            for result in results:
                if "analysis" in result:
                    issues = (
                        result["analysis"].get("issues", [])
                        if isinstance(result["analysis"], dict)
                        else []
                    )
                    all_issues.extend(issues)
                    for issue in issues:
                        savings = self._infer_max_savings(issue) if isinstance(issue, dict) else 0
                        if isinstance(savings, (int, float)):
                            total_savings += savings

            # Cross-document analysis: detect errors spanning multiple documents
            if len(documents) > 1:
                cross_issues = await self._run_cross_document_analysis(
                    documents=documents,
                    analysis_id=analysis_id,
                )
                for issue in cross_issues:
                    all_issues.append(issue)
                    savings = self._infer_max_savings(issue)
                    if isinstance(savings, (int, float)):
                        total_savings += savings

            log_with_context(
                logger,
                20,
                "💾 Saving analysis results",
                analysis_id=analysis_id,
                total_savings=total_savings,
                issues_count=len(all_issues),
                documents_analyzed=len(results),
            )

            # Prepare complete analysis results with all workflow outputs
            analysis_results = {
                "documents": results,
                "coverage_matrix": coverage_matrix,
                "normalized_transactions": normalized_transactions_list,
                "transaction_provenance": transaction_provenance,
            }

            # Save results to database
            await self.db.save_analysis_results(
                analysis_id=analysis_id,
                results=analysis_results,
                coverage_matrix=coverage_matrix,
                total_savings=total_savings,
                issues_count=len(all_issues),
            )

            # Insert individual issues
            if all_issues:
                logger.info(f"💾 Inserting {len(all_issues)} issues into database...")
                issues_to_insert = []
                for i, issue in enumerate(all_issues):
                    # Find which document this issue belongs to.
                    # Cross-document issues have source="cross_document" and no owner doc.
                    document_id = issue.get("document_id")  # may be pre-set for cross-doc issues
                    if document_id is None:
                        for result in results:
                            if "analysis" in result and isinstance(result["analysis"], dict):
                                if issue in result["analysis"].get("issues", []):
                                    document_id = result.get("document_id")
                                    break

                    issues_to_insert.append(
                        {
                            "document_id": document_id,
                            "issue_type": issue.get("type", "unknown"),
                            "summary": issue.get("summary", ""),
                            "evidence": issue.get("evidence", ""),
                            "code": issue.get("code", f"ISSUE-{i+1}"),
                            "recommended_action": issue.get("recommended_action", ""),
                            "max_savings": self._infer_max_savings(issue),
                            "confidence": issue.get("confidence", "medium"),
                            "source": issue.get("source", "llm"),
                            "metadata": issue.get("metadata", {}),
                        }
                    )

                await self.db.insert_issues(analysis_id, issues_to_insert)
                logger.info("✅ Issues inserted successfully")

            # Update analysis status to completed in database
            await self.db.update_analysis_status(analysis_id, "completed")

            log_with_context(
                logger,
                20,
                "🎉 Analysis completed successfully!",
                analysis_id=analysis_id,
                user_id=user_id,
                total_savings=total_savings,
                issues_count=len(all_issues),
                documents_analyzed=len(results),
            )

            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "total_savings": total_savings,
                "issues_count": len(all_issues),
                "documents_analyzed": len(results),
            }

        except Exception as e:
            import traceback

            tb_str = traceback.format_exc()
            log_with_context(
                logger,
                40,
                f"❌ Analysis workflow failed: {type(e).__name__}",
                analysis_id=analysis_id,
                user_id=user_id,
                error=str(e),
            )
            logger.error(f"Full traceback:\n{tb_str}")
            logger.exception("Analysis workflow failed")

            # Save error to database
            await self.db.update_analysis_status(analysis_id, "failed", error_message=str(e))
            return {"analysis_id": analysis_id, "status": "failed", "error": str(e)}

    async def _check_for_images(self, document_ids: List[str], user_id: str) -> bool:
        """Check if any documents are images."""
        for doc_id in document_ids:
            try:
                doc = await self.db.get_document(doc_id, user_id)
                if doc and doc.get("content_type", "").startswith("image/"):
                    return True
            except Exception as e:
                log_with_context(
                    logger, 30, "⚠️  Error checking document type", document_id=doc_id, error=str(e)
                )
                continue
        return False

    async def _run_multimodal_analysis(
        self, analysis_id: str, document_ids: List[str], user_id: str, provider: str
    ) -> Dict[str, Any]:
        """Run analysis when the batch includes image documents (PNG/JPG/etc).

        The legacy MultimodalAnalysisService called StorageService.download_document()
        which never existed, causing all downloads to silently fail.  This
        replacement routes each document to the correct pipeline:
          - text/plain, application/pdf  → orchestrator (same as text-only path)
          - image/*                       → GPT-4o vision (reads bill as image)
        Cross-document heuristics run after all per-doc passes complete.
        """
        try:
            from medbilldozer.core.orchestrator_agent import OrchestratorAgent
            from medbilldozer.providers.provider_registry import (
                ProviderRegistry,
                register_providers,
            )

            register_providers()
            import os

            try:
                from medbilldozer.providers.medgemma_ensemble_provider import (
                    MedGemmaEnsembleProvider,
                )

                ens = MedGemmaEnsembleProvider.__new__(MedGemmaEnsembleProvider)
                ens.enable_openai = False
                if os.getenv("HF_ENDPOINT_BASE"):
                    from medbilldozer.providers.medgemma_hosted_provider import (
                        MedGemmaHostedProvider,
                    )

                    ens.medgemma = MedGemmaHostedProvider()
                else:
                    from medbilldozer.providers.openai_analysis_provider import (
                        OpenAIAnalysisProvider,
                    )

                    ens.medgemma = OpenAIAnalysisProvider("gpt-4o-mini")
                ProviderRegistry.register("medgemma-ensemble", ens)
            except Exception:  # nosec B110 - intentional silent fallback
                pass

            effective_provider = (
                provider if provider in ProviderRegistry.list() else "medgemma-ensemble"
            )

            # --- Classify documents ---
            text_doc_metas: list = []
            image_doc_metas: list = []
            for doc_id in document_ids:
                doc_meta = await self.db.get_document(doc_id, user_id)
                if not doc_meta:
                    continue
                if doc_meta.get("content_type", "").startswith("image/"):
                    image_doc_metas.append(doc_meta)
                else:
                    text_doc_metas.append(doc_meta)

            results: list = []
            all_issues: list = []
            total_savings: float = 0.0

            # --- Analyze text documents via orchestrator ---
            for doc_meta in text_doc_metas:
                doc_id = doc_meta["document_id"]
                doc_started_at = datetime.utcnow().isoformat()
                try:
                    gcs_path = doc_meta.get("gcs_path") or doc_meta.get("file_path", "")
                    content_type = doc_meta.get("content_type", "text/plain")
                    raw_text = ""
                    if gcs_path:
                        try:
                            if content_type.startswith("text/"):
                                raw_text = await self.storage.download_text(
                                    bucket_name=self.storage.documents_bucket,
                                    blob_path=gcs_path,
                                )
                            else:
                                raw_text = await self._extract_text_from_pdf(gcs_path, doc_id)
                        except Exception:
                            raw_text = doc_meta.get("extracted_text", "") or ""

                    if not raw_text or len(raw_text.strip()) < 20:
                        results.append(
                            {
                                "document_id": doc_id,
                                "filename": doc_meta["filename"],
                                "error": "insufficient text",
                                "status": "failed",
                                "raw_text": "",
                            }
                        )
                        continue

                    orchestrator = OrchestratorAgent(analyzer_override=effective_provider)
                    orch_result = orchestrator.run(raw_text)
                    analysis_dict = self._serialize_analysis(orch_result.get("analysis"))

                    doc_result = {
                        "document_id": doc_id,
                        "filename": doc_meta["filename"],
                        "facts": orch_result.get("facts", {}),
                        "analysis": analysis_dict,
                        "raw_text": raw_text,
                    }
                    results.append(doc_result)

                    for iss in analysis_dict.get("issues", []):
                        savings = self._infer_max_savings(iss)
                        all_issues.append({**iss, "document_id": doc_id})
                        if isinstance(savings, (int, float)):
                            total_savings += savings

                    try:
                        await self.db.update_document_extracted_text(
                            document_id=doc_id, extracted_text=raw_text
                        )
                    except Exception:  # nosec B110 - non-critical text cache; analysis continues
                        pass

                except Exception as text_err:
                    log_with_context(
                        logger,
                        40,
                        f"❌ Text doc analysis failed: {text_err}",
                        analysis_id=analysis_id,
                        document_id=doc_id,
                    )
                    results.append(
                        {
                            "document_id": doc_id,
                            "filename": doc_meta.get("filename", ""),
                            "error": str(text_err),
                            "status": "failed",
                            "raw_text": "",
                        }
                    )
                finally:
                    await self.db.update_document_progress(
                        analysis_id=analysis_id,
                        document_id=doc_id,
                        phase="complete",
                        started_at=doc_started_at,
                    )

            # --- Analyze image documents with GPT-4o vision ---
            for doc_meta in image_doc_metas:
                doc_id = doc_meta["document_id"]
                doc_started_at = datetime.utcnow().isoformat()
                try:
                    vision_issues = await self._analyze_image_with_vision(doc_meta, analysis_id)
                    doc_result = {
                        "document_id": doc_id,
                        "filename": doc_meta["filename"],
                        "analysis": {
                            "issues": vision_issues,
                            "meta": {"source": "vision"},
                        },
                        "raw_text": "",
                    }
                    results.append(doc_result)
                    for iss in vision_issues:
                        savings = self._infer_max_savings(iss)
                        all_issues.append({**iss, "document_id": doc_id})
                        if isinstance(savings, (int, float)):
                            total_savings += savings
                except Exception as img_err:
                    log_with_context(
                        logger,
                        40,
                        f"❌ Image doc analysis failed: {img_err}",
                        analysis_id=analysis_id,
                        document_id=doc_id,
                    )
                    results.append(
                        {
                            "document_id": doc_id,
                            "filename": doc_meta.get("filename", ""),
                            "error": str(img_err),
                            "status": "failed",
                            "raw_text": "",
                        }
                    )
                finally:
                    await self.db.update_document_progress(
                        analysis_id=analysis_id,
                        document_id=doc_id,
                        phase="complete",
                        started_at=doc_started_at,
                    )

            # --- Cross-document analysis ---
            cross_docs = [
                {
                    "document_id": r["document_id"],
                    "filename": r["filename"],
                    "raw_text": r["raw_text"],
                }
                for r in results
                if r.get("raw_text")
            ]
            if len(cross_docs) > 1:
                cross_issues = await self._run_cross_document_analysis(
                    documents=cross_docs, analysis_id=analysis_id
                )
                for iss in cross_issues:
                    all_issues.append(iss)
                    savings = self._infer_max_savings(iss)
                    if isinstance(savings, (int, float)):
                        total_savings += savings

            # --- Save combined results ---
            combined_results = {
                "documents": results,
                "analysis_type": "multimodal",
                "documents_analyzed": {
                    "text": len(text_doc_metas),
                    "images": len(image_doc_metas),
                },
            }
            await self.db.save_analysis_results(
                analysis_id=analysis_id,
                results=combined_results,
                coverage_matrix=None,
                total_savings=total_savings,
                issues_count=len(all_issues),
            )

            if all_issues:
                issues_to_insert = []
                for i, iss in enumerate(all_issues):
                    issues_to_insert.append(
                        {
                            "document_id": iss.get("document_id"),
                            "issue_type": iss.get("type", "unknown"),
                            "summary": iss.get("summary", ""),
                            "evidence": iss.get("evidence", ""),
                            "code": iss.get("code") or f"ISSUE-{i + 1}",
                            "recommended_action": iss.get(
                                "recommended_action", "Review this charge."
                            ),
                            "max_savings": self._infer_max_savings(iss),
                            "confidence": iss.get("confidence", "medium"),
                            "source": iss.get("source", "analysis"),
                            "metadata": {},
                        }
                    )
                await self.db.insert_issues(analysis_id, issues_to_insert)

            await self.db.update_analysis_status(analysis_id, "completed")
            return {"analysis_id": analysis_id, "status": "completed"}

        except Exception as e:
            log_with_context(
                logger,
                40,
                f"❌ Multimodal analysis failed: {type(e).__name__}",
                analysis_id=analysis_id,
                user_id=user_id,
                error=str(e),
            )
            logger.exception("Multimodal analysis failed")
            await self.db.update_analysis_status(analysis_id, "failed", error_message=str(e))
            return {"analysis_id": analysis_id, "status": "failed", "error": str(e)}

    async def _analyze_image_with_vision(self, doc_meta: dict, analysis_id: str) -> list:
        """Analyze a medical bill image with GPT-4o vision.

        Downloads the image from GCS and asks GPT-4o to read the bill and
        identify billing errors, returning issues in the same dict format
        as the text-based orchestrator pipeline.
        """
        import base64
        import json as _json

        doc_id = doc_meta["document_id"]
        gcs_path = doc_meta.get("gcs_path") or doc_meta.get("file_path", "")
        content_type = doc_meta.get("content_type", "image/png")

        if not gcs_path:
            log_with_context(
                logger,
                30,
                "⚠️  No GCS path for image doc",
                analysis_id=analysis_id,
                document_id=doc_id,
            )
            return []

        try:
            image_bytes = await self.storage.download_bytes(
                bucket_name=self.storage.documents_bucket, blob_path=gcs_path
            )
        except Exception as dl_err:
            log_with_context(
                logger,
                30,
                f"⚠️  Image download failed: {dl_err}",
                analysis_id=analysis_id,
                document_id=doc_id,
            )
            return []

        image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

        billing_prompt = """You are a healthcare billing expert. Carefully read ALL text in this medical bill image and identify billing errors.

ISSUE TYPES TO DETECT:
1. duplicate_charge: Same CPT code billed multiple times on the same date
2. overbilling: Unusually high charges or excessive facility fees (>$500)
3. coding_error: Procedure coded at higher complexity than documented
4. unbundling: Related services billed separately instead of as a bundle
5. gender_mismatch: Procedures for anatomy the patient doesn't have
6. age_inappropriate_procedure: Procedures outside recommended age ranges
7. anatomical_contradiction: Procedures on absent or removed organs
8. procedure_inconsistent_with_health_history: No supporting diagnosis
9. diagnosis_procedure_mismatch: Procedure doesn't match the diagnosis
10. temporal_violation: Procedures violating medical timelines

Return ONLY a valid JSON array. If no issues: []
[{"type":"issue_type","summary":"brief description","evidence":"exact text/amounts from bill","code":"CPT code or null","max_savings":0.00}]"""

        try:
            from openai import OpenAI

            client = OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                max_tokens=2000,
                messages=[
                    {
                        "role": "system",
                        "content": "You analyze healthcare billing images and return ONLY valid JSON arrays. No prose.",
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{content_type};base64,{image_b64}",
                                    "detail": "high",
                                },
                            },
                            {"type": "text", "text": billing_prompt},
                        ],
                    },
                ],
            )

            content = response.choices[0].message.content or "[]"
            import re as _re

            content = _re.sub(r"```(?:json)?\s*", "", content).strip().rstrip("`").strip()
            raw_issues = _json.loads(content)
            if not isinstance(raw_issues, list):
                raw_issues = []

            issues = []
            for item in raw_issues:
                max_savings = item.get("max_savings")
                if max_savings is not None:
                    try:
                        max_savings = float(max_savings)
                    except (TypeError, ValueError):
                        max_savings = None
                issues.append(
                    {
                        "type": item.get("type", "billing_error"),
                        "summary": item.get("summary", ""),
                        "evidence": item.get("evidence", ""),
                        "code": item.get("code"),
                        "max_savings": max_savings,
                        "source": "vision",
                        "confidence": 0.8,
                    }
                )

            log_with_context(
                logger,
                20,
                f"✅ Vision analysis found {len(issues)} issue(s)",
                analysis_id=analysis_id,
                document_id=doc_id,
            )
            return issues

        except Exception as vision_err:
            log_with_context(
                logger,
                30,
                f"⚠️  Vision analysis error: {vision_err}",
                analysis_id=analysis_id,
                document_id=doc_id,
            )
            return []

    def _serialize_analysis(self, analysis_obj) -> dict:
        """Convert an AnalysisResult dataclass to a JSON-serializable dict.

        The orchestrator returns an AnalysisResult dataclass, not a plain dict.
        Dict-style membership checks (``"issues" in analysis_obj``) raise TypeError
        on a dataclass, so we normalize it here before any further processing.
        """
        if isinstance(analysis_obj, dict):
            return analysis_obj
        if analysis_obj is None:
            return {"issues": [], "meta": {}}

        issues_list = []
        for iss in getattr(analysis_obj, "issues", None) or []:
            if isinstance(iss, dict):
                issues_list.append(iss)
            else:
                issues_list.append(
                    {
                        "type": getattr(iss, "type", "unknown"),
                        "summary": getattr(iss, "summary", ""),
                        "evidence": getattr(iss, "evidence", None),
                        "code": getattr(iss, "code", None),
                        "date": getattr(iss, "date", None),
                        "recommended_action": getattr(iss, "recommended_action", None),
                        "max_savings": getattr(iss, "max_savings", None),
                        "source": getattr(iss, "source", "llm"),
                        "confidence": getattr(iss, "confidence", None),
                    }
                )

        return {
            "issues": issues_list,
            "meta": getattr(analysis_obj, "meta", {}) or {},
        }

    @staticmethod
    def _infer_max_savings(issue: dict) -> float:
        """Extract max_savings from issue text when the LLM left it as 0 or null.

        For duplicate charges the savings equals the duplicated charge amount,
        which is always mentioned in the summary or evidence text.
        """
        existing = issue.get("max_savings")
        if existing and isinstance(existing, (int, float)) and existing > 0:
            return float(existing)

        import re

        text = f"{issue.get('summary', '')} {issue.get('evidence', '')}"
        amounts = re.findall(r"\$\s*([\d,]+(?:\.\d{2})?)", text)
        for raw in amounts:
            try:
                val = float(raw.replace(",", ""))
                if val > 0:
                    return val
            except ValueError:
                continue
        return 0.0

    async def _run_cross_document_analysis(
        self,
        documents: list,
        analysis_id: str,
    ) -> list:
        """Analyze all documents together to find cross-document billing errors.

        Combines document texts with ``--- DOCUMENT N ---`` markers (which the
        medgemma-ensemble duplicate-charge heuristic already understands) and
        submits them to the registered ensemble provider.  Issues found here are
        tagged with ``source="cross_document"`` so the UI can surface them
        distinctly.
        """
        if len(documents) < 2:
            return []

        try:
            from medbilldozer.providers.llm_interface import ProviderRegistry

            provider = ProviderRegistry.get("medgemma-ensemble") or ProviderRegistry.get(
                "gpt-4o-mini"
            )
            if not provider:
                return []

            # Build combined text using the marker format the ensemble heuristics expect
            parts = []
            for i, doc in enumerate(documents, 1):
                parts.append(f"--- DOCUMENT {i}: {doc['filename']} ---\n{doc['raw_text']}")
            combined_text = "\n\n".join(parts)

            cross_doc_prefix = (
                "[MULTI-DOCUMENT CROSS-ANALYSIS MODE]\n"
                "Analyze ALL documents together and identify issues that span ACROSS documents:\n"
                "- duplicate_charge: same procedure/CPT billed in multiple documents on the same date\n"
                "- cross_bill_discrepancy: same service appears with different amounts across documents\n"
                "- drug_drug_interaction: conflicting medications mentioned across documents\n"
                "- temporal_violation: impossible timelines or contradictory dates across documents\n"
                "- diagnosis_procedure_mismatch: procedure in one doc contradicts diagnosis in another\n"
                "Only flag issues with evidence from MULTIPLE documents.\n\n"
            )

            result = provider.analyze_document(cross_doc_prefix + combined_text)

            cross_issues = []
            for iss in self._serialize_analysis(result).get("issues", []):
                iss_copy = dict(iss)
                iss_copy["source"] = "cross_document"
                iss_copy.setdefault("document_id", None)
                cross_issues.append(iss_copy)

            log_with_context(
                logger,
                20,
                f"✅ Cross-document analysis found {len(cross_issues)} issue(s)",
                analysis_id=analysis_id,
                document_count=len(documents),
            )
            return cross_issues

        except Exception as e:
            log_with_context(
                logger,
                30,
                f"⚠️  Cross-document analysis failed: {str(e)}",
                analysis_id=analysis_id,
            )
            return []

    async def _extract_text_from_pdf(self, gcs_path: str, document_id: str) -> str:
        """
        Extract text from PDF using PyPDF2 (on-demand extraction).

        Args:
            gcs_path: Path to PDF in GCS
            document_id: Document ID for logging

        Returns:
            Extracted text string, or empty string if extraction fails
        """
        try:
            import io

            import PyPDF2

            # Download PDF bytes from GCS
            pdf_bytes = await self.storage.download_bytes(
                bucket_name=self.storage.documents_bucket, blob_path=gcs_path
            )

            log_with_context(
                logger,
                20,
                f"📥 Downloaded PDF for extraction ({len(pdf_bytes)} bytes)",
                document_id=document_id,
            )

            # Extract text using PyPDF2
            log_with_context(logger, 20, "📄 Extracting text with PyPDF2", document_id=document_id)

            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            extracted_text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"

            extracted_text = extracted_text.strip()

            log_with_context(
                logger,
                20,
                f"✅ Extracted {len(extracted_text)} chars from {len(pdf_reader.pages)} pages",
                document_id=document_id,
            )

            return extracted_text

        except Exception as e:
            log_with_context(
                logger,
                40,
                f"❌ PDF extraction error: {str(e)}",
                document_id=document_id,
                error=str(e),
            )
            return ""


# Singleton instance
_analysis_service: AnalysisService | None = None


def get_analysis_service() -> AnalysisService:
    """Get or create AnalysisService singleton."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service
