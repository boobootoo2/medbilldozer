"""
MedBillDozer - Production Streamlit Interface with Password Protection
This page connects to the deployed Cloud Run backend
"""

import streamlit as st
import requests
from typing import Optional
import os

# Configuration - Load from Streamlit secrets (preferred) or environment variables
try:
    API_BASE_URL = st.secrets.get("API_BASE_URL", "https://medbilldozer-api-360553024921.us-central1.run.app")
    APP_PASSWORD = st.secrets.get("APP_ACCESS_PASSWORD", os.getenv("APP_ACCESS_PASSWORD"))
except Exception:
    API_BASE_URL = "https://medbilldozer-api-360553024921.us-central1.run.app"
    APP_PASSWORD = os.getenv("APP_ACCESS_PASSWORD")

# Validate that password is set
if not APP_PASSWORD or APP_PASSWORD == "CHANGE_THIS_TO_YOUR_SECURE_PASSWORD":
    st.error("""
    ⚠️ **APP_ACCESS_PASSWORD not configured!**

    Please set your password in one of these locations:

    1. **Streamlit Secrets** (recommended):
       - Edit `.streamlit/secrets.toml`
       - Set: `APP_ACCESS_PASSWORD = "YourSecurePassword"`

    2. **Environment Variable**:
       - Set: `export APP_ACCESS_PASSWORD="YourSecurePassword"`

    See `.streamlit/README.md` for detailed instructions.
    """)
    st.stop()


def check_password() -> bool:
    """Returns True if the user entered the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == APP_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # First run or password not correct
    if "password_correct" not in st.session_state:
        # Show input for password
        st.text_input(
            "🔒 Enter Password",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.caption("Contact admin for access credentials")
        return False

    # Password incorrect
    elif not st.session_state["password_correct"]:
        st.text_input(
            "🔒 Enter Password",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.error("😕 Password incorrect")
        return False

    # Password correct
    return True


def get_firebase_token() -> Optional[str]:
    """Get Firebase authentication token (stub - implement proper auth)"""
    # TODO: Implement proper Firebase authentication
    # For now, return None - you'd need to implement Firebase auth flow
    return st.session_state.get("firebase_token")


def upload_document(file, token: str):
    """Upload document to backend API"""
    try:
        # Step 1: Request signed upload URL
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        response = requests.post(
            f"{API_BASE_URL}/api/documents/upload-url",
            json={
                "filename": file.name,
                "content_type": file.type
            },
            headers=headers
        )

        if response.status_code != 200:
            st.error(f"Failed to get upload URL: {response.text}")
            return None

        data = response.json()
        upload_url = data["upload_url"]
        document_id = data["document_id"]

        # Step 2: Upload to GCS
        upload_response = requests.put(
            upload_url,
            data=file.getvalue(),
            headers={"Content-Type": file.type}
        )

        if upload_response.status_code != 200:
            st.error(f"Failed to upload file: {upload_response.text}")
            return None

        # Step 3: Confirm upload
        confirm_response = requests.post(
            f"{API_BASE_URL}/api/documents/confirm",
            json={
                "document_id": document_id,
                "gcs_path": data["gcs_path"],
                "size_bytes": len(file.getvalue())
            },
            headers=headers
        )

        if confirm_response.status_code != 200:
            st.error(f"Failed to confirm upload: {confirm_response.text}")
            return None

        return document_id

    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return None


def main():
    """Main application interface"""
    st.set_page_config(
        page_title="MedBillDozer - Production",
        page_icon="💊",
        layout="wide"
    )

    # Password protection
    if not check_password():
        st.stop()

    # Show logged in interface
    st.title("💊 MedBillDozer - Production Interface")
    st.markdown("### AI-Powered Medical Billing Analysis")

    # Check backend health
    try:
        health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            st.success(f"✅ Backend Connected: {API_BASE_URL}")
        else:
            st.warning("⚠️ Backend responding but may have issues")
    except Exception as e:
        st.error(f"❌ Cannot connect to backend: {str(e)}")

    # Sidebar for authentication
    with st.sidebar:
        st.header("🔐 Authentication")

        # Simple auth status
        if "firebase_token" not in st.session_state:
            st.info("📱 For full features, log in via the web app:")
            st.markdown(f"[Open Web App](https://frontend-five-umber-24.vercel.app)")

            # Alternative: Guest mode
            if st.button("Continue as Guest"):
                st.session_state["firebase_token"] = None
                st.rerun()
        else:
            st.success("✅ Authenticated")
            if st.button("Logout"):
                del st.session_state["firebase_token"]
                st.rerun()

    # Main content
    tab1, tab2, tab3 = st.tabs(["📄 Upload Documents", "📊 View Documents", "🔗 Web App"])

    with tab1:
        st.header("Upload Medical Documents")

        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "png", "jpg", "jpeg", "txt"],
            help="Upload medical bills, EOBs, or clinical images"
        )

        if uploaded_file is not None:
            col1, col2 = st.columns([3, 1])

            with col1:
                st.info(f"📎 **File:** {uploaded_file.name} ({uploaded_file.size} bytes)")

            with col2:
                if st.button("Upload", type="primary"):
                    with st.spinner("Uploading..."):
                        token = get_firebase_token()
                        document_id = upload_document(uploaded_file, token)

                        if document_id:
                            st.success(f"✅ Uploaded! Document ID: {document_id}")
                            st.balloons()
                        else:
                            st.error("Upload failed")

    with tab2:
        st.header("Your Documents")
        st.info("🔗 View and manage documents in the web app")
        st.markdown(f"[Open Document Manager](https://frontend-five-umber-24.vercel.app)")

    with tab3:
        st.header("Full Web Application")
        st.markdown("""
        For the complete experience with all features:

        - ✅ Google Authentication
        - ✅ Document Management
        - ✅ AI Analysis
        - ✅ Interactive Dashboard

        **Visit:** [https://frontend-five-umber-24.vercel.app](https://frontend-five-umber-24.vercel.app)
        """)

        # Embed the web app in iframe (optional)
        if st.checkbox("Embed Web App Here"):
            st.components.v1.iframe(
                "https://frontend-five-umber-24.vercel.app",
                height=800,
                scrolling=True
            )


if __name__ == "__main__":
    main()
