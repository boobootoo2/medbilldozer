"""Analysis service wrapping existing MedBillDozer orchestrator."""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

# Add parent directory to path for importing medbilldozer modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.services.storage_service import get_storage_service
from app.services.db_service import get_db_service


class AnalysisService:
    """
    Wraps existing OrchestratorAgent for async analysis execution.
    Integrates with GCS for document retrieval and Supabase for persistence.
    """

    def __init__(self):
        """Initialize analysis service."""
        print("🔧 Initializing AnalysisService...")
        self.storage = get_storage_service()
        print("  ✓ StorageService initialized")
        self.db = get_db_service()
        print("  ✓ DBService initialized")
        from app.services.multimodal_analysis_service import MultimodalAnalysisService
        print("  ⏳ Initializing MultimodalAnalysisService...")
        self.multimodal_service = MultimodalAnalysisService()
        print("  ✓ MultimodalAnalysisService initialized")
        print("✅ AnalysisService ready")

    async def run_analysis(
        self,
        analysis_id: str,
        document_ids: List[str],
        user_id: str,
        provider: str = "medgemma-ensemble"
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
            # Update status to processing
            await self.db.update_analysis_status(analysis_id, "processing")

            # Check if any documents are images (multimodal analysis needed)
            has_images = await self._check_for_images(document_ids, user_id)

            # Use multimodal service if images are present
            if has_images:
                return await self._run_multimodal_analysis(
                    analysis_id, document_ids, user_id, provider
                )

            # Otherwise, continue with text-only analysis
            # Import existing medbilldozer modules
            from medbilldozer.core.orchestrator_agent import OrchestratorAgent
            from medbilldozer.core.coverage_matrix import build_coverage_matrix
            from medbilldozer.providers.provider_registry import register_providers, ProviderRegistry

            # Ensure provider is registered
            register_providers()
            if provider not in ProviderRegistry.list():
                provider = "smart"  # Fallback to smart mode

            # Download documents from GCS and prepare for analysis
            documents = []
            for doc_id in document_ids:
                doc_meta = await self.db.get_document(doc_id, user_id)
                if not doc_meta:
                    continue

                # Download raw text from GCS
                try:
                    raw_text = await self.storage.download_text(
                        bucket_name=self.storage.documents_bucket,
                        blob_path=doc_meta['gcs_path']
                    )
                except Exception as e:
                    # If download fails, use extracted_text from metadata
                    raw_text = doc_meta.get('extracted_text', '')

                documents.append({
                    "document_id": doc_id,
                    "raw_text": raw_text,
                    "filename": doc_meta['filename'],
                    "document_type": doc_meta.get('document_type'),
                    "facts": {}
                })

            if not documents:
                await self.db.update_analysis_status(
                    analysis_id,
                    "failed",
                    error_message="No documents found"
                )
                return {"status": "failed", "error": "No documents found"}

            # Run orchestrator for each document (REUSE EXISTING CODE)
            results = []
            for idx, doc in enumerate(documents, 1):
                doc_id = doc['document_id']
                doc_started_at = datetime.utcnow().isoformat()

                try:
                    orchestrator = OrchestratorAgent(
                        analyzer_override=provider,
                        profile_context=None  # TODO: load user profile from DB
                    )

                    # Create progress callback that updates database
                    def progress_callback(workflow_log, step_status):
                        """Update database with current phase."""
                        try:
                            # Use asyncio to call async method from sync callback
                            import asyncio
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(
                                self.db.update_document_progress(
                                    analysis_id=analysis_id,
                                    document_id=doc_id,
                                    phase=step_status,
                                    started_at=doc_started_at
                                )
                            )
                            loop.close()
                        except Exception as e:
                            print(f"⚠️  Progress update failed: {e}")

                    # Initialize progress as "starting"
                    await self.db.update_document_progress(
                        analysis_id=analysis_id,
                        document_id=doc_id,
                        phase="pre_extraction_active",
                        started_at=doc_started_at
                    )

                    # Run analysis with progress callback
                    result = orchestrator.run(doc['raw_text'], progress_callback=progress_callback)

                    # Mark as complete
                    await self.db.update_document_progress(
                        analysis_id=analysis_id,
                        document_id=doc_id,
                        phase="complete",
                        started_at=doc_started_at
                    )

                    results.append({
                        "document_id": doc_id,
                        "filename": doc['filename'],
                        "facts": result.get('facts', {}),
                        "analysis": result.get('analysis', {}),
                        "orchestration": result.get('_orchestration', {}),
                        "progress": {
                            "phase": "complete",
                            "started_at": doc_started_at,
                            "completed_at": datetime.utcnow().isoformat()
                        }
                    })
                except Exception as e:
                    # Mark as failed
                    await self.db.update_document_progress(
                        analysis_id=analysis_id,
                        document_id=doc_id,
                        phase="failed",
                        started_at=doc_started_at
                    )

                    results.append({
                        "document_id": doc_id,
                        "filename": doc['filename'],
                        "error": str(e),
                        "status": "failed",
                        "progress": {
                            "phase": "failed",
                            "started_at": doc_started_at,
                            "failed_at": datetime.utcnow().isoformat(),
                            "error_message": str(e)
                        }
                    })

            # Build coverage matrix (REUSE EXISTING CODE)
            coverage_matrix = None
            try:
                if len(results) > 1:
                    coverage_matrix = build_coverage_matrix(results)
            except Exception as e:
                print(f"Coverage matrix failed: {e}")

            # Calculate total savings and issue count
            total_savings = 0
            all_issues = []
            for result in results:
                if 'analysis' in result and 'issues' in result['analysis']:
                    issues = result['analysis']['issues']
                    all_issues.extend(issues)
                    for issue in issues:
                        savings = issue.get('max_savings', 0)
                        if isinstance(savings, (int, float)):
                            total_savings += savings

            # Save results to database
            await self.db.save_analysis_results(
                analysis_id=analysis_id,
                results=results,
                coverage_matrix=coverage_matrix,
                total_savings=total_savings,
                issues_count=len(all_issues)
            )

            # Insert individual issues
            if all_issues:
                issues_to_insert = []
                for i, issue in enumerate(all_issues):
                    # Find which document this issue belongs to
                    document_id = None
                    for result in results:
                        if 'analysis' in result and issue in result['analysis'].get('issues', []):
                            document_id = result.get('document_id')
                            break

                    issues_to_insert.append({
                        "document_id": document_id,
                        "issue_type": issue.get('type', 'unknown'),
                        "summary": issue.get('summary', ''),
                        "evidence": issue.get('evidence', ''),
                        "code": issue.get('code', f'ISSUE-{i+1}'),
                        "recommended_action": issue.get('recommended_action', ''),
                        "max_savings": issue.get('max_savings', 0),
                        "confidence": issue.get('confidence', 'medium'),
                        "source": issue.get('source', 'llm'),
                        "metadata": issue.get('metadata', {})
                    })

                await self.db.insert_issues(analysis_id, issues_to_insert)

            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "total_savings": total_savings,
                "issues_count": len(all_issues),
                "documents_analyzed": len(results)
            }

        except Exception as e:
            # Save error to database
            await self.db.update_analysis_status(
                analysis_id,
                "failed",
                error_message=str(e)
            )
            return {
                "analysis_id": analysis_id,
                "status": "failed",
                "error": str(e)
            }

    async def _check_for_images(self, document_ids: List[str], user_id: str) -> bool:
        """Check if any documents are images."""
        for doc_id in document_ids:
            try:
                doc = await self.db.get_document(doc_id, user_id)
                if doc and doc.get('content_type', '').startswith('image/'):
                    return True
            except Exception as e:
                print(f"Error checking document {doc_id}: {e}")
                continue
        return False

    async def _run_multimodal_analysis(
        self,
        analysis_id: str,
        document_ids: List[str],
        user_id: str,
        provider: str
    ) -> Dict[str, Any]:
        """Run multimodal analysis combining text and images."""
        try:
            # Execute multimodal analysis
            results = await self.multimodal_service.analyze_documents(
                document_ids=document_ids,
                user_id=user_id,
                provider=provider
            )

            # Extract summary metrics
            summary = results.get('summary', {})
            total_savings = summary.get('total_potential_savings', 0)
            total_issues = summary.get('total_issues', 0)

            # Save results to database
            await self.db.save_analysis_results(
                analysis_id=analysis_id,
                results=results,
                coverage_matrix=results.get('cross_document_findings'),
                total_savings=total_savings,
                issues_count=total_issues
            )

            # Insert individual issues
            all_issues = []

            # Add billing issues from text analysis
            for text_result in results.get('text_analysis', []):
                if 'analysis' in text_result and 'issues' in text_result['analysis']:
                    for issue in text_result['analysis']['issues']:
                        all_issues.append({
                            'document_id': text_result.get('document_id'),
                            'issue_type': issue.get('type', 'billing_error'),
                            'summary': issue.get('summary', ''),
                            'evidence': issue.get('evidence', ''),
                            'code': issue.get('code', ''),
                            'recommended_action': issue.get('recommended_action', ''),
                            'max_savings': issue.get('max_savings', 0),
                            'confidence': issue.get('confidence', 'medium'),
                            'source': 'text_analysis',
                            'metadata': issue.get('metadata', {})
                        })

            # Add clinical issues from image analysis
            for image_result in results.get('image_analysis', []):
                findings = image_result.get('findings', {})
                for issue in findings.get('issues', []):
                    all_issues.append({
                        'document_id': image_result.get('document_id'),
                        'issue_type': 'clinical_finding',
                        'summary': issue,
                        'evidence': f"Medical image: {image_result.get('filename')}",
                        'code': '',
                        'recommended_action': 'Review clinical findings',
                        'max_savings': 0,
                        'confidence': 'high',
                        'source': 'image_analysis',
                        'metadata': findings
                    })

            # Add cross-reference inconsistencies
            for inconsistency in results.get('cross_reference_findings', {}).get('inconsistencies', []):
                all_issues.append({
                    'document_id': None,  # Cross-document issue
                    'issue_type': inconsistency.get('type', 'inconsistency'),
                    'summary': inconsistency.get('description', ''),
                    'evidence': inconsistency.get('evidence', ''),
                    'code': '',
                    'recommended_action': inconsistency.get('recommended_action', ''),
                    'max_savings': inconsistency.get('potential_savings', 0),
                    'confidence': inconsistency.get('severity', 'medium'),
                    'source': 'cross_reference',
                    'metadata': inconsistency
                })

            if all_issues:
                await self.db.insert_issues(analysis_id, all_issues)

            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "total_savings": total_savings,
                "issues_count": total_issues,
                "documents_analyzed": len(document_ids),
                "multimodal": True
            }

        except Exception as e:
            # Save error to database
            await self.db.update_analysis_status(
                analysis_id,
                "failed",
                error_message=str(e)
            )
            return {
                "analysis_id": analysis_id,
                "status": "failed",
                "error": str(e)
            }


# Singleton instance
_analysis_service: AnalysisService | None = None


def get_analysis_service() -> AnalysisService:
    """Get or create AnalysisService singleton."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service
