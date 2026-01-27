"""Interactive API Documentation Page for Streamlit

A Swagger-like interactive API documentation interface that runs entirely
within Streamlit, allowing users to explore and test API endpoints.
"""

import streamlit as st
import json
from typing import Dict, Any, Optional
from datetime import datetime

# Import API functions
from _modules.ingest.api import (
    ingest_document,
    list_imports,
    get_normalized_data,
    get_import_status,
)
from _modules.data.fictional_entities import get_all_fictional_entities


def render_api_docs_page():
    """Main API documentation page with interactive testing"""
    
    st.title("🔌 MedBillDozer API Documentation")
    st.markdown("""
    **Interactive API Explorer** - Test all endpoints directly in your browser.
    
    This is a Plaid-like healthcare data ingestion API for demo purposes.
    No authentication required for testing.
    """)
    
    # Sidebar navigation
    st.sidebar.title("📚 API Endpoints")
    
    endpoint = st.sidebar.radio(
        "Select an endpoint:",
        [
            "🏠 Overview",
            "🏥 List Entities",
            "📥 Ingest Document",
            "📋 List Imports",
            "📊 Get Normalized Data",
            "🔍 Get Import Status"
        ]
    )
    
    # Main content area
    if endpoint == "🏠 Overview":
        render_overview()
    elif endpoint == "🏥 List Entities":
        render_list_entities()
    elif endpoint == "📥 Ingest Document":
        render_ingest_document()
    elif endpoint == "📋 List Imports":
        render_list_imports()
    elif endpoint == "📊 Get Normalized Data":
        render_get_data()
    elif endpoint == "🔍 Get Import Status":
        render_get_status()


def render_overview():
    """Render API overview page"""
    
    st.header("API Overview")
    
    st.markdown("""
    ### About
    The MedBillDozer API provides programmatic access to healthcare data ingestion
    and normalization services. Similar to how Plaid connects to banks, this API
    connects to insurance companies and healthcare providers.
    
    ### Base URL
    ```
    Demo Mode: Direct function calls (no HTTP server needed)
    Production: https://api.medbilldozer.com/v1
    ```
    
    ### Authentication
    Currently **no authentication** required for demo. Production would use:
    - OAuth 2.0
    - API Keys
    - JWT tokens
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **✅ Available Endpoints**
        - List Entities
        - Ingest Document
        - List Imports
        - Get Normalized Data
        - Get Import Status
        """)
    
    with col2:
        st.warning("""
        **⚠️ Demo Limitations**
        - In-memory storage
        - No persistence
        - Single-user mode
        - No rate limiting
        """)
    
    st.markdown("---")
    st.subheader("📖 Quick Start Example")
    
    st.code("""
# 1. List available entities
entities = list_entities()

# 2. Ingest a document
response = ingest_document({
    "user_id": "user_12345",
    "entity_type": "insurance",
    "entity_id": "ins_blueshield_ca",
    "num_line_items": 10
})
job_id = response.job_id

# 3. Check status
status = get_import_status(job_id)

# 4. Get normalized data
data = get_normalized_data("user_12345")
    """, language="python")


def render_list_entities():
    """Render List Entities endpoint"""
    
    st.header("🏥 List Entities")
    
    # Endpoint info
    render_endpoint_badge("GET", "List Available Healthcare Entities")
    
    st.markdown("""
    Get all available insurance companies and healthcare providers
    that can be used for data ingestion.
    """)
    
    # Parameters
    with st.expander("📝 Parameters", expanded=True):
        entity_type_filter = st.selectbox(
            "Entity Type (optional)",
            ["All", "insurance", "provider"],
            help="Filter by entity type"
        )
    
    # Try it out button
    st.markdown("---")
    if st.button("▶️ Execute", key="exec_list_entities", type="primary"):
        with st.spinner("Fetching entities..."):
            try:
                entities = get_all_fictional_entities()
                
                # Apply filter
                if entity_type_filter != "All":
                    entities = [e for e in entities if e.get("type") == entity_type_filter]
                
                st.success(f"✅ Found {len(entities)} entities")
                
                # Response
                render_response_section(200, {
                    "success": True,
                    "total": len(entities),
                    "entities": entities
                })
                
                # Visual display
                st.markdown("### Entity List")
                for entity in entities:
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 3])
                        with col1:
                            st.markdown(f"**{entity['name']}**")
                        with col2:
                            badge_color = "🔵" if entity['type'] == "insurance" else "🟢"
                            st.markdown(f"{badge_color} {entity['type']}")
                        with col3:
                            st.caption(f"ID: `{entity['id']}`")
                        st.markdown("---")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Code examples
    render_code_examples("list_entities", """
# Python
entities = get_all_fictional_entities()
insurance_only = [e for e in entities if e['type'] == 'insurance']
    """, """
// JavaScript
fetch('/api/v1/entities?entity_type=insurance')
  .then(res => res.json())
  .then(data => console.log(data.entities));
    """)


def render_ingest_document():
    """Render Ingest Document endpoint"""
    
    st.header("📥 Ingest Document")
    
    render_endpoint_badge("POST", "Import Healthcare Data")
    
    st.markdown("""
    Ingest healthcare data from an insurance company or provider.
    This simulates connecting to the entity and importing their data.
    """)
    
    # Request body
    with st.expander("📝 Request Body", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.text_input(
                "User ID *",
                value="user_12345",
                help="Unique identifier for the user"
            )
            
            entity_type = st.selectbox(
                "Entity Type *",
                ["insurance", "provider"],
                help="Type of healthcare entity"
            )
        
        with col2:
            # Get entities for dropdown
            all_entities = get_all_fictional_entities()
            # Extract the appropriate list based on entity_type
            if entity_type == 'insurance':
                filtered_entities = all_entities['insurance']
            else:  # provider
                filtered_entities = all_entities['providers']
            entity_names = {f"{e['name']} ({e['id']})": e['id'] for e in filtered_entities}
            
            selected_entity = st.selectbox(
                "Entity *",
                options=list(entity_names.keys()),
                help="Select the healthcare entity"
            )
            entity_id = entity_names[selected_entity]
            
            num_line_items = st.number_input(
                "Number of Line Items",
                min_value=1,
                max_value=100,
                value=10,
                help="How many line items to generate"
            )
        
        raw_text = st.text_area(
            "Raw Document Text (optional)",
            placeholder="Paste medical bill or insurance document text here...",
            help="Optional: Provide raw document text to parse"
        )
    
    # Execute button
    st.markdown("---")
    if st.button("▶️ Execute", key="exec_ingest", type="primary"):
        with st.spinner("Ingesting document..."):
            try:
                payload = {
                    "user_id": user_id,
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "num_line_items": num_line_items,
                }
                
                if raw_text:
                    payload["raw_text"] = raw_text
                
                # Call API
                response = ingest_document(payload)
                
                if response.success:
                    st.success(f"✅ {response.message}")
                    
                    # Show response
                    render_response_section(201, {
                        "success": response.success,
                        "job_id": response.job_id,
                        "message": response.message,
                        "documents_created": response.documents_created,
                        "line_items_created": response.line_items_created,
                        "timestamp": response.timestamp
                    })
                    
                    # Quick actions
                    st.info(f"💡 **Job ID:** `{response.job_id}` - Use this to check status or retrieve data")
                    
                else:
                    st.error(f"❌ Ingestion failed: {response.message}")
                    if response.errors:
                        st.warning("Errors: " + ", ".join(response.errors))
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Code examples
    render_code_examples("ingest_document", f"""
# Python
response = ingest_document({{
    "user_id": "{user_id}",
    "entity_type": "{entity_type}",
    "entity_id": "{entity_id}",
    "num_line_items": {num_line_items}
}})
print(f"Job ID: {{response.job_id}}")
    """, f"""
// JavaScript
fetch('/api/v1/ingest/document', {{
  method: 'POST',
  headers: {{'Content-Type': 'application/json'}},
  body: JSON.stringify({{
    user_id: '{user_id}',
    entity_type: '{entity_type}',
    entity_id: '{entity_id}',
    num_line_items: {num_line_items}
  }})
}}).then(res => res.json());
    """)


def render_list_imports():
    """Render List Imports endpoint"""
    
    st.header("📋 List Imports")
    
    render_endpoint_badge("GET", "Get All User Imports")
    
    st.markdown("""
    Retrieve all import jobs for a specific user, including status and statistics.
    """)
    
    # Parameters
    with st.expander("📝 Parameters", expanded=True):
        user_id = st.text_input(
            "User ID *",
            value="user_12345",
            help="User ID to query imports for"
        )
    
    # Execute
    st.markdown("---")
    if st.button("▶️ Execute", key="exec_list_imports", type="primary"):
        with st.spinner("Fetching imports..."):
            try:
                response = list_imports(user_id)
                
                if response.success:
                    st.success(f"✅ Found {response.total_imports} import(s)")
                    
                    render_response_section(200, {
                        "success": response.success,
                        "user_id": response.user_id,
                        "total_imports": response.total_imports,
                        "imports": [vars(imp) for imp in response.imports]
                    })
                    
                    # Visual display
                    if response.total_imports > 0:
                        st.markdown("### Import History")
                        for imp in response.imports:
                            with st.container():
                                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                                with col1:
                                    st.markdown(f"**{imp.entity_name}**")
                                    st.caption(f"Job ID: `{imp.job_id}`")
                                with col2:
                                    st.caption(f"📅 {imp.created_at}")
                                with col3:
                                    status_icon = "✅" if imp.status == "completed" else "⏳"
                                    st.markdown(f"{status_icon} {imp.status}")
                                with col4:
                                    st.metric("Items", imp.line_items_count)
                                st.markdown("---")
                    else:
                        st.info("No imports found for this user. Try ingesting a document first.")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    render_code_examples("list_imports", f"""
# Python
response = list_imports("{user_id}")
for import_job in response.imports:
    print(f"{{import_job.job_id}}: {{import_job.status}}")
    """, f"""
// JavaScript
fetch('/api/v1/imports?user_id={user_id}')
  .then(res => res.json())
  .then(data => console.log(data.imports));
    """)


def render_get_data():
    """Render Get Normalized Data endpoint"""
    
    st.header("📊 Get Normalized Data")
    
    render_endpoint_badge("GET", "Retrieve Normalized Line Items")
    
    st.markdown("""
    Get all normalized healthcare line items for a user. Optionally filter by job ID.
    """)
    
    # Parameters
    with st.expander("📝 Parameters", expanded=True):
        user_id = st.text_input(
            "User ID *",
            value="user_12345",
            help="User ID to retrieve data for"
        )
        
        job_id = st.text_input(
            "Job ID (optional)",
            placeholder="e.g., import_abc123",
            help="Filter by specific import job"
        )
    
    # Execute
    st.markdown("---")
    if st.button("▶️ Execute", key="exec_get_data", type="primary"):
        with st.spinner("Fetching data..."):
            try:
                response = get_normalized_data(user_id, job_id if job_id else None)
                
                if response.success:
                    st.success(f"✅ Retrieved {response.total_line_items} line item(s)")
                    
                    render_response_section(200, {
                        "success": response.success,
                        "user_id": response.user_id,
                        "total_line_items": response.total_line_items,
                        "line_items": response.line_items[:5],  # Show first 5
                        "metadata": response.metadata
                    })
                    
                    # Visual display
                    if response.total_line_items > 0:
                        st.markdown("### Line Items Preview")
                        
                        # Display as dataframe
                        import pandas as pd
                        df = pd.DataFrame(response.line_items)
                        
                        # Select key columns if they exist
                        display_cols = []
                        for col in ['service_date', 'description', 'amount', 'cpt_code', 'provider_name']:
                            if col in df.columns:
                                display_cols.append(col)
                        
                        if display_cols:
                            st.dataframe(df[display_cols], use_container_width=True)
                        else:
                            st.dataframe(df, use_container_width=True)
                        
                        # Download button
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv,
                            file_name=f"healthcare_data_{user_id}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No data found for this user. Try ingesting a document first.")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    render_code_examples("get_data", f"""
# Python
response = get_normalized_data("{user_id}")
print(f"Total items: {{response.total_line_items}}")
for item in response.line_items:
    print(item['description'], item['amount'])
    """, f"""
// JavaScript
fetch('/api/v1/data?user_id={user_id}')
  .then(res => res.json())
  .then(data => console.log(data.line_items));
    """)


def render_get_status():
    """Render Get Import Status endpoint"""
    
    st.header("🔍 Get Import Status")
    
    render_endpoint_badge("GET", "Check Import Job Status")
    
    st.markdown("""
    Get detailed status information about a specific import job.
    """)
    
    # Parameters
    with st.expander("📝 Parameters", expanded=True):
        job_id = st.text_input(
            "Job ID *",
            placeholder="e.g., import_abc123",
            help="The import job ID to check"
        )
    
    # Execute
    st.markdown("---")
    if st.button("▶️ Execute", key="exec_get_status", type="primary"):
        if not job_id:
            st.warning("⚠️ Please enter a Job ID")
        else:
            with st.spinner("Checking status..."):
                try:
                    response = get_import_status(job_id)
                    
                    if response.success:
                        status_icon = {
                            "completed": "✅",
                            "processing": "⏳",
                            "pending": "🕐",
                            "failed": "❌"
                        }.get(response.status, "ℹ️")
                        
                        st.success(f"{status_icon} Status: **{response.status.upper()}**")
                        
                        render_response_section(200, {
                            "success": response.success,
                            "job_id": response.job_id,
                            "status": response.status,
                            "import_job": response.import_job
                        })
                        
                        # Visual display
                        if response.import_job:
                            job = response.import_job
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Documents", job.get('documents_count', 0))
                            with col2:
                                st.metric("Line Items", job.get('line_items_count', 0))
                            with col3:
                                st.metric("Status", job.get('status', 'unknown'))
                    else:
                        st.error(f"❌ Job not found: {job_id}")
                        if response.error_message:
                            st.warning(response.error_message)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    render_code_examples("get_status", f"""
# Python
response = get_import_status("{job_id or 'import_abc123'}")
print(f"Status: {{response.status}}")
if response.import_job:
    print(f"Line items: {{response.import_job['line_items_count']}}")
    """, f"""
// JavaScript
fetch('/api/v1/imports/{job_id or 'import_abc123'}')
  .then(res => res.json())
  .then(data => console.log(data.status));
    """)


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def render_endpoint_badge(method: str, title: str):
    """Render endpoint method badge"""
    method_color = {
        "GET": "#61AFFE",
        "POST": "#49CC90",
        "PUT": "#FCA130",
        "DELETE": "#F93E3E"
    }.get(method, "#999")
    
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <span style="background: {method_color}; color: white; padding: 0.25rem 0.75rem; 
                     border-radius: 4px; font-weight: 600; font-size: 0.875rem; 
                     margin-right: 1rem;">{method}</span>
        <span style="font-size: 1.1rem; color: #666;">{title}</span>
    </div>
    """, unsafe_allow_html=True)


def render_response_section(status_code: int, response_data: Dict[str, Any]):
    """Render response section with JSON"""
    st.markdown("### 📤 Response")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        status_color = "green" if status_code < 300 else "red"
        st.markdown(f"**Status:** :{status_color}[{status_code}]")
    
    with col2:
        st.caption("Response Time: ~50ms")
    
    # JSON response
    with st.expander("View JSON Response", expanded=True):
        st.json(response_data)


def render_code_examples(endpoint_name: str, python_code: str, js_code: str):
    """Render code examples in multiple languages"""
    st.markdown("---")
    st.markdown("### 💻 Code Examples")
    
    tab1, tab2, tab3 = st.tabs(["🐍 Python", "🟨 JavaScript", "📝 cURL"])
    
    with tab1:
        st.code(python_code.strip(), language="python")
    
    with tab2:
        st.code(js_code.strip(), language="javascript")
    
    with tab3:
        # Generate cURL example (simplified)
        st.code(f"""
# Example cURL command
curl -X GET "http://localhost:8000/api/v1/{endpoint_name}" \\
  -H "Accept: application/json"
        """.strip(), language="bash")


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    # For standalone testing
    st.set_page_config(
        page_title="MedBillDozer API Docs",
        page_icon="🔌",
        layout="wide"
    )
    render_api_docs_page()
