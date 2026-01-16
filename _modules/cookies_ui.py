# _modules/cookies_ui.py

import json
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager
from streamlit_cookies_manager.cookie_manager import CookiesNotReady

COOKIE_KEY = "mdb_privacy"

DEFAULT_STATE = {
    "privacyAccepted": False,
    "cookies": {
        "essential": True,
        "preferences": False,
        "analytics": False,
    },
}

def get_cookie_manager() -> EncryptedCookieManager:
    # Always render the component
    if "cookies" not in st.session_state:
        st.session_state.cookies = EncryptedCookieManager(
            prefix="medbilldozer",
            password="medbilldozer-demo-secret",
        )
    return st.session_state.cookies


def get_privacy_state() -> dict:
    """
    Safe cookie read.
    Returns defaults if cookies are not ready yet.
    NEVER raises CookiesNotReady.
    """
    cm = get_cookie_manager()

    try:
        raw = cm.get(COOKIE_KEY)
    except CookiesNotReady:
        # First render: browser has not responded yet
        return DEFAULT_STATE.copy()

    if not raw:
        return DEFAULT_STATE.copy()

    try:
        return {**DEFAULT_STATE, **json.loads(raw)}
    except Exception:
        return DEFAULT_STATE.copy()

from streamlit_cookies_manager.cookie_manager import CookiesNotReady
import json

def set_privacy_state(state: dict) -> bool:
    """
    Attempts to persist privacy state.
    Returns True if saved, False if cookies not ready yet.
    NEVER raises.
    """
    cm = get_cookie_manager()
    try:
        cm[COOKIE_KEY] = json.dumps(state)
        return True
    except CookiesNotReady:
        return False


def privacy_accepted() -> bool:
    return get_privacy_state().get("privacyAccepted", False)
