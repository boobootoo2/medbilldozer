"""Analysis service wrapping existing MedBillDozer orchestrator."""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio

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
        self.storage = get_storage_service()
        self.db = get_db_service()

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

            # Import existing medbilldozer modules
            from src.medbilldozer.core.orchestrator_agent import OrchestratorAgent
            from src.medbilldozer.core.coverage_matrix import build_coverage_matrix
            from src.medbilldozer.providers.provider_registry import get_provider_registry

            # Ensure provider is registered
            registry = get_provider_registry()
            if provider not in registry.list_providers():
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
            for doc in documents:
                try:
                    orchestrator = OrchestratorAgent(
                        analyzer_override=provider,
                        profile_context=None  # TODO: load user profile from DB
                    )

                    # Run analysis
                    result = orchestrator.run(doc['raw_text'])

                    results.append({
                        "document_id": doc['document_id'],
                        "filename": doc['filename'],
                        "facts": result.get('facts', {}),
                        "analysis": result.get('analysis', {}),
                        "orchestration": result.get('_orchestration', {})
                    })
                except Exception as e:
                    results.append({
                        "document_id": doc['document_id'],
                        "filename": doc['filename'],
                        "error": str(e),
                        "status": "failed"
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


# Singleton instance
_analysis_service: AnalysisService | None = None


def get_analysis_service() -> AnalysisService:
    """Get or create AnalysisService singleton."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service
