import json
import streamlit.components.v1 as components

from pathlib import Path

BILLDOZER_TOKEN = "BILLDOZER_v1"

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
    """
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