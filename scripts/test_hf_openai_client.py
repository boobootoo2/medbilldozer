"""
Quick test script to call the Hugging Face router via the OpenAI-compatible client.

Usage:
  export HF_TOKEN="..."
  python3 scripts/test_hf_openai_client.py

The script is defensive: it reports missing packages or environment variables and prints
any HTTP/SDK errors that occur.
"""

import os
import sys

try:
    from openai import OpenAI
except Exception as e:
    print("Missing OpenAI client library. Install with: pip install openai")
    print("Import error:", e)
    sys.exit(1)

HF_TOKEN = os.environ.get("HF_TOKEN") or os.environ.get("HF_API_TOKEN")
if not HF_TOKEN:
    print("Missing HF_TOKEN or HF_API_TOKEN environment variable. Export your Hugging Face token as HF_TOKEN or HF_API_TOKEN.")
    sys.exit(1)

client = None
try:
    client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=HF_TOKEN)
except Exception as e:
    print("Failed to construct OpenAI client:", e)
    sys.exit(1)

try:
    completion = client.chat.completions.create(
        model="google/gemma-3-27b-it:scaleway",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in one sentence."},
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"}
                    }
                ],
            }
        ],
    )
    # print the entire response for debugging, but truncate if very long
    import json
    out = json.dumps(completion, default=str, indent=2)
    print(out[:8000])
except Exception as e:
    print("Request failed:")
    print(type(e), e)
    # If the SDK raises a response-like exception, try to print more details
    try:
        import traceback
        traceback.print_exc()
    except Exception:
        pass
    sys.exit(1)

print('\n--- success ---\n')
print(completion.choices[0].message if getattr(completion, 'choices', None) else completion)
