"""Supabase database service."""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.config import settings
from supabase import Client, create_client

logger = logging.getLogger(__name__)


class DBService:
    """Handles database operations with Supabase."""

    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(
            settings.supabase_url, settings.supabase_service_role_key
        )

    # ========================================================================
    # USER PROFILES
    # ========================================================================

    async def create_or_update_user(
        self,
        firebase_uid: str,
        email: str,
        display_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create or update user profile - using simple select/insert to avoid PostgREST cache issues."""
        try:
            print(f"🔄 Checking if user exists: {firebase_uid}")

            # Check if user already exists
            existing = (
                self.client.table("user_profiles")
                .select("*")
                .eq("firebase_uid", firebase_uid)
                .execute()
            )

            if existing and existing.data and len(existing.data) > 0:
                print(f"✅ User already exists: {email}")
                # Skip updating last_login_at due to PostgREST cache issue
                # Just return the existing user
                return existing.data[0]
            else:
                print(f"🔄 Creating new user with minimal fields: {email}")
                # Generate user_id in Python since PostgREST cache won't use the database default
                user_id = str(uuid.uuid4())
                new_user = (
                    self.client.table("user_profiles")
                    .insert({"user_id": user_id, "firebase_uid": firebase_uid, "email": email})
                    .execute()
                )

                if new_user.data:
                    print(f"✅ Created minimal user profile: {email}")
                    return new_user.data[0]
                else:
                    raise Exception("Insert returned no data")

        except Exception as e:
            print(f"❌ User creation error: {e}")
            raise Exception(f"Failed to create/update user: {e}")

    async def get_user_by_firebase_uid(self, firebase_uid: str) -> Optional[Dict[str, Any]]:
        """Get user by Firebase UID."""
        result = (
            self.client.table("user_profiles")
            .select("*")
            .eq("firebase_uid", firebase_uid)
            .execute()
        )
        return result.data[0] if result.data else None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by user ID."""
        result = self.client.table("user_profiles").select("*").eq("user_id", user_id).execute()
        return result.data[0] if result.data else None

    # ========================================================================
    # DOCUMENTS
    # ========================================================================

    async def insert_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert document metadata."""
        result = self.client.table("documents").insert(document_data).execute()
        return result.data[0]

    async def get_document(self, document_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID and user ID."""
        result = (
            self.client.table("documents")
            .select("*")
            .eq("document_id", document_id)
            .eq("user_id", user_id)
            .execute()
        )
        return result.data[0] if result.data else None

    async def list_user_documents(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List all documents for a user."""
        result = (
            self.client.table("documents")
            .select("*")
            .eq("user_id", user_id)
            .order("uploaded_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return result.data

    async def update_document_status(
        self, document_id: str, status: str, error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update document status."""
        update_data = {"status": status}
        if error_message:
            update_data["error_message"] = error_message

        result = (
            self.client.table("documents")
            .update(update_data)
            .eq("document_id", document_id)
            .execute()
        )
        return result.data[0]

    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete document."""
        self.client.table("documents").delete().eq("document_id", document_id).eq(
            "user_id", user_id
        ).execute()
        return True

    async def update_document_extracted_text(
        self, document_id: str, extracted_text: str
    ) -> Dict[str, Any]:
        """
        Update document with extracted text (for caching on-demand extraction).

        Args:
            document_id: Document ID
            extracted_text: Extracted text content to cache

        Returns:
            Updated document record
        """
        logger.info(
            f"💾 Caching extracted text for document {document_id[:8]}... ({len(extracted_text)} chars)"
        )

        result = (
            self.client.table("documents")
            .update({"extracted_text": extracted_text})
            .eq("document_id", document_id)
            .execute()
        )

        return result.data[0] if result.data else {}

    async def list_user_documents_enhanced(
        self,
        user_id: str,
        profile_id: Optional[str] = None,
        action: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List documents with enhanced filtering by profile and action.

        Args:
            user_id: User ID
            profile_id: Filter by profile ID in metadata
            action: Filter by specific action status
            status: Filter by document status
            limit: Max results
            offset: Pagination offset

        Returns:
            List of document dictionaries
        """
        query = self.client.table("documents").select("*").eq("user_id", user_id)

        # Filter by profile ID in metadata JSONB
        if profile_id:
            query = query.eq("metadata->>profile_id", profile_id)

        # Filter by action
        if action:
            query = query.eq("action", action)

        # Filter by status
        if status:
            query = query.eq("status", status)

        result = query.order("uploaded_at", desc=True).range(offset, offset + limit - 1).execute()

        return result.data

    async def update_document_action(
        self,
        document_id: str,
        action: Optional[str],
        action_notes: Optional[str] = None,
        action_updated_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update document action status.

        Args:
            document_id: Document ID
            action: Action status (ignored/followup/resolved) or None to clear
            action_notes: Optional notes
            action_updated_by: User ID who updated

        Returns:
            Updated document dictionary
        """
        update_data: Dict[str, Any] = {
            "action": action,
            "action_notes": action_notes,
            "action_updated_by": action_updated_by,
        }

        # If action is None, also clear action_date
        if action is None:
            update_data["action_date"] = None

        result = (
            self.client.table("documents")
            .update(update_data)
            .eq("document_id", document_id)
            .execute()
        )

        return result.data[0] if result.data else {}

    async def update_document_metadata(
        self, document_id: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update document metadata (merges with existing).

        Args:
            document_id: Document ID
            metadata: Metadata dictionary to merge

        Returns:
            Updated document dictionary
        """
        result = (
            self.client.table("documents")
            .update({"metadata": metadata})
            .eq("document_id", document_id)
            .execute()
        )

        return result.data[0] if result.data else {}

    async def get_document_issue_counts(self, document_ids: List[str]) -> Dict[str, Dict[str, int]]:
        """
        Get issue counts for multiple documents.

        Args:
            document_ids: List of document IDs

        Returns:
            Dict mapping document_id to:
            {
                'total': total issues,
                'high_confidence_open': high confidence open issues,
                'open': total open issues
            }
        """
        if not document_ids:
            return {}

        try:
            # Query issues for these documents
            result = (
                self.client.table("issues")
                .select("document_id, confidence, metadata")
                .in_("document_id", document_ids)
                .execute()
            )

            issues_data = result.data if result.data else []
        except Exception as e:
            # If issues table doesn't exist or query fails, return empty dict
            # This handles 404 errors when table doesn't exist or no issues are found
            logger.warning(f"Issues table query failed (table may not exist): {e}")
            return {}

        # Aggregate counts
        counts: Dict[str, Dict[str, int]] = {}
        for issue in issues_data:
            doc_id = str(issue["document_id"])
            if doc_id not in counts:
                counts[doc_id] = {"total": 0, "high_confidence_open": 0, "open": 0}

            counts[doc_id]["total"] += 1

            # Check if issue is open (default to open if not specified)
            issue_status = (
                issue.get("metadata", {}).get("status", "open") if issue.get("metadata") else "open"
            )

            if issue_status == "open":
                counts[doc_id]["open"] += 1

                if issue.get("confidence") == "high":
                    counts[doc_id]["high_confidence_open"] += 1

        return counts

    async def get_document_action_statistics(
        self, user_id: str, profile_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get statistics on document actions for a user/profile.

        Uses the document_action_statistics view.

        Args:
            user_id: User ID
            profile_id: Optional profile ID to filter by

        Returns:
            Statistics dictionary
        """
        query = self.client.table("document_action_statistics").select("*").eq("user_id", user_id)

        if profile_id:
            query = query.eq("profile_id", profile_id)

        result = query.execute()

        if result.data:
            return result.data[0]

        # Return empty stats if no data
        return {
            "user_id": user_id,
            "profile_id": profile_id,
            "profile_name": None,
            "total_documents": 0,
            "followup_count": 0,
            "ignored_count": 0,
            "resolved_count": 0,
            "pending_count": 0,
            "completed_count": 0,
            "followup_amount": 0.0,
            "resolved_amount": 0.0,
            "total_amount": 0.0,
            "last_action_date": None,
            "last_upload_date": None,
        }

    # ========================================================================
    # ANALYSES
    # ========================================================================

    async def create_analysis(
        self,
        analysis_id: str,
        user_id: str,
        document_ids: List[str],
        provider: str = "medgemma-ensemble",
    ) -> Dict[str, Any]:
        """Create new analysis record."""
        # Get document metadata to initialize results with filenames
        logger.info(f"🔍 Fetching metadata for {len(document_ids)} documents: {document_ids}")
        documents = []
        for doc_id in document_ids:
            doc_result = (
                self.client.table("documents")
                .select("document_id, filename")
                .eq("document_id", doc_id)
                .eq("user_id", user_id)
                .execute()
            )

            logger.info(
                f"📄 Document query for {doc_id}: found {len(doc_result.data) if doc_result.data else 0} results"
            )

            if doc_result.data:
                doc = doc_result.data[0]
                documents.append(
                    {
                        "document_id": doc["document_id"],
                        "filename": doc["filename"],
                        "progress": {
                            "phase": "pre_extraction_active",
                            "started_at": None,
                            "updated_at": None,
                        },
                    }
                )
            else:
                logger.warning(f"⚠️  Document {doc_id} not found in database for user {user_id}")

        logger.info(f"✅ Initialized results array with {len(documents)} documents")

        result = (
            self.client.table("analyses")
            .insert(
                {
                    "analysis_id": analysis_id,
                    "user_id": user_id,
                    "document_ids": document_ids,
                    "provider": provider,
                    "status": "queued",
                    "results": documents,  # Initialize with document placeholders
                }
            )
            .execute()
        )

        created_analysis = result.data[0]
        logger.info(
            f"✨ Created analysis {analysis_id} with results: {created_analysis.get('results', [])}"
        )
        return created_analysis

    async def get_analysis(self, analysis_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis by ID."""
        result = (
            self.client.table("analyses")
            .select("*")
            .eq("analysis_id", analysis_id)
            .eq("user_id", user_id)
            .execute()
        )
        return result.data[0] if result.data else None

    async def update_analysis_status(
        self, analysis_id: str, status: str, error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update analysis status."""
        update_data = {"status": status}

        # Note: started_at and completed_at columns may not exist in all Supabase instances
        # Commenting out until schema migration is confirmed
        # if status == "processing" and not update_data.get("started_at"):
        #     update_data["started_at"] = datetime.utcnow().isoformat()
        #
        # if status == "completed":
        #     update_data["completed_at"] = datetime.utcnow().isoformat()

        if error_message:
            update_data["error_message"] = error_message

        result = (
            self.client.table("analyses")
            .update(update_data)
            .eq("analysis_id", analysis_id)
            .execute()
        )
        return result.data[0]

    async def update_document_progress(
        self,
        analysis_id: str,
        document_id: str,
        phase: str,
        started_at: Optional[str] = None,
        workflow_log: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Update progress for a specific document during analysis.

        Args:
            analysis_id: Analysis ID
            document_id: Document ID
            phase: Current phase (pre_extraction_active, extraction_active, etc.)
            started_at: ISO timestamp when this document started processing
            workflow_log: Optional workflow log dict with detailed step information
        """
        # Get current analysis
        result = (
            self.client.table("analyses").select("results").eq("analysis_id", analysis_id).execute()
        )

        if not result.data:
            return {}

        current_results = result.data[0].get("results") or []

        # Find or create document entry in results
        doc_found = False
        for doc_result in current_results:
            if doc_result.get("document_id") == document_id:
                doc_result["progress"] = {
                    "phase": phase,
                    "updated_at": datetime.utcnow().isoformat(),
                }
                if started_at:
                    doc_result["progress"]["started_at"] = started_at
                if workflow_log:
                    doc_result["progress"]["workflow_log"] = workflow_log
                doc_found = True
                break

        if not doc_found:
            # Create new document entry with progress
            progress_obj = {
                "phase": phase,
                "started_at": started_at or datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            if workflow_log:
                progress_obj["workflow_log"] = workflow_log

            current_results.append({"document_id": document_id, "progress": progress_obj})

        # Update the results in database
        update_result = (
            self.client.table("analyses")
            .update({"results": current_results})
            .eq("analysis_id", analysis_id)
            .execute()
        )

        return update_result.data[0] if update_result.data else {}

    async def save_analysis_results(
        self,
        analysis_id: str,
        results: Dict[str, Any],
        coverage_matrix: Optional[Dict[str, Any]] = None,
        total_savings: float = 0,
        issues_count: int = 0,
    ) -> Dict[str, Any]:
        """Save analysis results."""
        result = (
            self.client.table("analyses")
            .update(
                {
                    "status": "completed",
                    "results": results,
                    "coverage_matrix": coverage_matrix,
                    "total_savings_detected": total_savings,
                    "issues_count": issues_count,
                    "completed_at": datetime.utcnow().isoformat(),
                }
            )
            .eq("analysis_id", analysis_id)
            .execute()
        )
        return result.data[0]

    async def list_user_analyses(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List all analyses for a user."""
        result = (
            self.client.table("analyses")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return result.data

    # ========================================================================
    # ISSUES
    # ========================================================================

    async def insert_issues(
        self, analysis_id: str, issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Insert multiple issues."""
        issues_data = [{"analysis_id": analysis_id, **issue} for issue in issues]
        result = self.client.table("issues").insert(issues_data).execute()
        return result.data

    async def get_issue(self, issue_id: str) -> Optional[Dict[str, Any]]:
        """Get single issue by ID."""
        result = self.client.table("issues").select("*").eq("issue_id", issue_id).execute()
        return result.data[0] if result.data else None

    async def get_issues_by_analysis(
        self, analysis_id: str, status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all issues for an analysis, optionally filtered by status."""
        query = (
            self.client.table("issues")
            .select("*")
            .eq("analysis_id", analysis_id)
            .order("created_at", desc=True)
        )

        if status_filter:
            query = query.eq("status", status_filter)

        result = query.execute()
        return result.data

    async def update_issue_status(
        self,
        issue_id: str,
        status: str,
        notes: Optional[str] = None,
        updated_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update issue status and optionally add notes."""
        update_data = {"status": status, "status_updated_at": datetime.utcnow().isoformat()}

        if notes is not None:
            update_data["notes"] = notes

        if updated_by:
            update_data["status_updated_by"] = updated_by

        result = self.client.table("issues").update(update_data).eq("issue_id", issue_id).execute()
        return result.data[0] if result.data else {}

    async def update_issue_notes(self, issue_id: str, notes: str) -> Dict[str, Any]:
        """Update notes for an issue."""
        result = (
            self.client.table("issues").update({"notes": notes}).eq("issue_id", issue_id).execute()
        )
        return result.data[0] if result.data else {}

    async def get_issue_statistics(self, analysis_id: str) -> Dict[str, Any]:
        """Get issue statistics for an analysis."""
        # Get all issues for the analysis
        issues = await self.get_issues_by_analysis(analysis_id)

        # Calculate statistics
        stats = {
            "open_count": 0,
            "follow_up_count": 0,
            "resolved_count": 0,
            "ignored_count": 0,
            "open_potential_savings": 0,
            "follow_up_potential_savings": 0,
            "resolved_savings": 0,
        }

        for issue in issues:
            status = issue.get("status", "open")
            savings = float(issue.get("max_savings", 0) or 0)

            if status == "open":
                stats["open_count"] += 1
                stats["open_potential_savings"] += savings
            elif status == "follow_up":
                stats["follow_up_count"] += 1
                stats["follow_up_potential_savings"] += savings
            elif status == "resolved":
                stats["resolved_count"] += 1
                stats["resolved_savings"] += savings
            elif status == "ignored":
                stats["ignored_count"] += 1

        return stats


# Singleton instance
_db_service: DBService | None = None


def get_db_service() -> DBService:
    """Get or create DBService singleton."""
    global _db_service
    if _db_service is None:
        _db_service = DBService()
    return _db_service
