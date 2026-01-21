"""Coverage matrix UI rendering.

Displays cross-document coverage relationships in a formatted table.
"""
# _modules/ui_coverage_matrix.py
import streamlit as st

def render_coverage_matrix(rows):
    """Render coverage matrix as a formatted dataframe.
    
    Shows receipts, FSA claims, and insurance payments side-by-side for comparison.
    
    Args:
        rows: List of CoverageRow objects
    """
    if not rows:
        st.caption("No cross-document coverage relationships found.")
        return

    st.markdown("## 🧾 Coverage Matrix")

    table = []
    for r in rows:
        table.append({
            "Item": r.description,
            "Date": r.date,
            "Receipt": f"${r.receipt_amount:.2f}" if r.receipt_amount else "—",
            "FSA": f"${r.fsa_amount:.2f}" if r.fsa_amount else "—",
            "Insurance": f"${r.insurance_amount:.2f}" if r.insurance_amount else "—",
            "Status": r.status,
        })

    st.dataframe(table, use_container_width=True)
