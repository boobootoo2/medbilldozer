# _modules/runtime_flags.py
import streamlit as st

def debug_enabled() -> bool:
    return st.query_params.get("debug") == "1"
