import json
import streamlit.components.v1 as components

BILLDOZER_TOKEN = "BILLDOZER_v1"


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

            // flush queued messages
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


def dispatch_widget_message(character: str, message: str):
    if not message:
        return  # 🔒 guard against None / empty

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
