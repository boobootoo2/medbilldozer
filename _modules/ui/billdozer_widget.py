import json
import streamlit.components.v1 as components

from pathlib import Path
from config import BILLDOZER_TOKEN

_WIDGET_HTML_CACHE = None

# --------------------------------------------------
# Widget HTML loader
# --------------------------------------------------


def get_billdozer_widget_html() -> str:
    """
    Loads and caches the Billdozer widget HTML.
    Injects Streamlit-safe CSS overrides.
    """
    global _WIDGET_HTML_CACHE

    if _WIDGET_HTML_CACHE is None:
        widget_path = (
            Path(__file__).parent.parent.parent
            / "static"
            / "bulldozer_animation.html"
        )

        html = widget_path.read_text(encoding="utf-8")

        css_override = """
        <style>
          .controls {
            display: none !important;
          }
        </style>
        """

        html = html.replace("</head>", css_override + "\n</head>")
        _WIDGET_HTML_CACHE = html

    return _WIDGET_HTML_CACHE

# --------------------------------------------------
# Bridge install (parent <-> iframe handshake)
# --------------------------------------------------


def install_billdozer_bridge():
    components.html(
        f"""
        <script>
        (function () {{
          const TOKEN = {json.dumps(BILLDOZER_TOKEN)};

          if (window.parent.__billdozerBridgeInstalled) return;
          window.parent.__billdozerBridgeInstalled = true;

          window.parent.__billdozerTargetWindow = null;
          window.parent.__billdozerMsgQueue = window.parent.__billdozerMsgQueue || [];

          window.parent.addEventListener("message", (e) => {{
            const data = e.data;
            if (!data || data.type !== "BILLDOZER_READY") return;
            if (data.token !== TOKEN) return;

            window.parent.__billdozerTargetWindow = e.source;
            console.log("[Billdozer bridge] READY received");

            const q = window.parent.__billdozerMsgQueue || [];
            while (q.length) {{
              e.source.postMessage(q.shift(), "*");
            }}
          }});

          console.log("[Billdozer bridge] installed");
        }})();
        </script>
        """,
        height=0,
    )


# --------------------------------------------------
# Message dispatcher
# --------------------------------------------------


def dispatch_widget_message(character: str, message: str):
    """
    Sends a speech message to the widget.
    Safely queues if the iframe is not ready yet.
    Also stores message in session state transcript.
    """
    import streamlit as st

    # Initialize transcript in session state
    if 'billdozer_transcript' not in st.session_state:
        st.session_state.billdozer_transcript = []

    # Add to transcript with timestamp
    from datetime import datetime
    st.session_state.billdozer_transcript.append({
        'timestamp': datetime.now().isoformat(),
        'character': character,
        'message': message
    })
    if not message:
        return  # Guard against None / empty

    components.html(
        f"""
        <script>
        (function () {{
          window.parent.__billdozerMsgQueue =
            window.parent.__billdozerMsgQueue || [];

          const payload = {{
            type: "CHARACTER_MESSAGE",
            payload: {{
              character: {json.dumps(character)},
              message: {json.dumps(message)}
            }}
          }};

          const target = window.parent.__billdozerTargetWindow;

          if (!target) {{
            console.warn("[Billdozer] target not ready, queued:", payload);
            window.parent.__billdozerMsgQueue.push(payload);
            return;
          }}

          target.postMessage(payload, "*");
          console.log("[Billdozer] sent:", payload);
        }})();
        </script>
        """,
        height=0,
    )


# --------------------------------------------------
# Sidebar widget renderer
# --------------------------------------------------


def render_billdozer_sidebar_widget():
    """Render billdozer widget in sidebar with bubble styling."""
    import streamlit as st

    if not st.session_state.get("show_billdozer_widget", False):
        return

    with st.sidebar:
        # Render widget in a styled bubble
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
            border-radius: 8px;
            padding: 16px;
            color: white;
            margin-bottom: 16px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-weight: 700; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">
                    BillDozer Status
                </div>
            </div>
        </div>
        # SECURITY: unsafe_allow_html=True is safe here because:
        # - Static HTML header for widget styling
        # - No user input or dynamic content
        # - Fixed text "BillDozer Status" with styling only
        """, unsafe_allow_html=True)

        # Render the actual widget iframe
        col_widget, col_close = st.columns([20, 1])

        with col_close:
            if st.button("✕", key="dismiss_billdozer_sidebar"):
                st.session_state.show_billdozer_widget = False

        with col_widget:
            components.html(
                get_billdozer_widget_html(),
                height=180,
                scrolling=False,
            )

