"""Supabase database service."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from app.config import settings


class DBService:
    """Handles database operations with Supabase."""

    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )

    # ========================================================================
    # USER PROFILES
    # ========================================================================

    async def create_or_update_user(
        self,
        firebase_uid: str,
        email: str,
        display_name: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create or update user profile."""
        try:
            # Try to find existing user
            result = self.client.table("user_profiles")\
                .select("*")\
                .eq("firebase_uid", firebase_uid)\
                .execute()

            if result.data:
                # Update existing
                user = self.client.table("user_profiles")\
                    .update({
                        "email": email,
                        "display_name": display_name,
                        "avatar_url": avatar_url,
                        "last_login_at": datetime.utcnow().isoformat()
                    })\
                    .eq("firebase_uid", firebase_uid)\
                    .execute()
                return user.data[0]
            else:
                # Create new
                user = self.client.table("user_profiles")\
                    .insert({
                        "firebase_uid": firebase_uid,
                        "email": email,
                        "display_name": display_name,
                        "avatar_url": avatar_url,
                        "last_login_at": datetime.utcnow().isoformat()
                    })\
                    .execute()
                return user.data[0]
        except Exception as e:
            raise Exception(f"Error creating/updating user: {e}")

    async def get_user_by_firebase_uid(self, firebase_uid: str) -> Optional[Dict[str, Any]]:
        """Get user by Firebase UID."""
        result = self.client.table("user_profiles")\
            .select("*")\
            .eq("firebase_uid", firebase_uid)\
            .execute()
        return result.data[0] if result.data else None

    # ========================================================================
    # DOCUMENTS
    # ========================================================================

    async def insert_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert document metadata."""
        result = self.client.table("documents")\
            .insert(document_data)\
            .execute()
        return result.data[0]

    async def get_document(
        self,
        document_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get document by ID and user ID."""
        result = self.client.table("documents")\
            .select("*")\
            .eq("document_id", document_id)\
            .eq("user_id", user_id)\
            .execute()
        return result.data[0] if result.data else None

    async def list_user_documents(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List all documents for a user."""
        result = self.client.table("documents")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("uploaded_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        return result.data

    async def update_document_status(
        self,
        document_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update document status."""
        update_data = {"status": status}
        if error_message:
            update_data["error_message"] = error_message

        result = self.client.table("documents")\
            .update(update_data)\
            .eq("document_id", document_id)\
            .execute()
        return result.data[0]

    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete document."""
        self.client.table("documents")\
            .delete()\
            .eq("document_id", document_id)\
            .eq("user_id", user_id)\
            .execute()
        return True

    # ========================================================================
    # ANALYSES
    # ========================================================================

    async def create_analysis(
        self,
        analysis_id: str,
        user_id: str,
        document_ids: List[str],
        provider: str = "medgemma-ensemble"
    ) -> Dict[str, Any]:
        """Create new analysis record."""
        result = self.client.table("analyses")\
            .insert({
                "analysis_id": analysis_id,
                "user_id": user_id,
                "document_ids": document_ids,
                "provider": provider,
                "status": "queued"
            })\
            .execute()
        return result.data[0]

    async def get_analysis(
        self,
        analysis_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get analysis by ID."""
        result = self.client.table("analyses")\
            .select("*")\
            .eq("analysis_id", analysis_id)\
            .eq("user_id", user_id)\
            .execute()
        return result.data[0] if result.data else None

    async def update_analysis_status(
        self,
        analysis_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update analysis status."""
        update_data = {"status": status}

        if status == "processing" and not update_data.get("started_at"):
            update_data["started_at"] = datetime.utcnow().isoformat()

        if status == "completed":
            update_data["completed_at"] = datetime.utcnow().isoformat()

        if error_message:
            update_data["error_message"] = error_message

        result = self.client.table("analyses")\
            .update(update_data)\
            .eq("analysis_id", analysis_id)\
            .execute()
        return result.data[0]

    async def save_analysis_results(
        self,
        analysis_id: str,
        results: Dict[str, Any],
        coverage_matrix: Optional[Dict[str, Any]] = None,
        total_savings: float = 0,
        issues_count: int = 0
    ) -> Dict[str, Any]:
        """Save analysis results."""
        result = self.client.table("analyses")\
            .update({
                "status": "completed",
                "results": results,
                "coverage_matrix": coverage_matrix,
                "total_savings_detected": total_savings,
                "issues_count": issues_count,
                "completed_at": datetime.utcnow().isoformat()
            })\
            .eq("analysis_id", analysis_id)\
            .execute()
        return result.data[0]

    async def list_user_analyses(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List all analyses for a user."""
        result = self.client.table("analyses")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        return result.data

    # ========================================================================
    # ISSUES
    # ========================================================================

    async def insert_issues(
        self,
        analysis_id: str,
        issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Insert multiple issues."""
        issues_data = [
            {
                "analysis_id": analysis_id,
                **issue
            }
            for issue in issues
        ]
        result = self.client.table("issues")\
            .insert(issues_data)\
            .execute()
        return result.data


# Singleton instance
_db_service: DBService | None = None


def get_db_service() -> DBService:
    """Get or create DBService singleton."""
    global _db_service
    if _db_service is None:
        _db_service = DBService()
    return _db_service
