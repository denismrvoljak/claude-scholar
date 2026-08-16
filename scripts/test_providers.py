"""Run every provider path in pdf_to_markdown.py against a mock HTTP endpoint.

Costs nothing and needs no API key: each SDK is pointed at a local server that
returns a canned, provider-shaped response.

Validates that for every provider the SDK method exists and accepts the
parameters used, the page image reaches the wire as base64, the system prompt
is attached, and the response parses back to the transcription text.

Does NOT validate that the live provider accepts the request — model IDs and
server-side validation can only be checked with a real key. If a provider path
breaks after an SDK upgrade, this is the fastest way to find out where.

Usage:
    pip install pypdfium2 pillow anthropic openai google-genai
    python scripts/test_providers.py [path/to/any.pdf]
"""
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pdf_to_markdown as P

RECEIVED = {}
MARKER = "## Slide 1\n\n$E = mc^2$"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        path = self.path
        if "/messages" in path:
            provider, payload = "anthropic", {
                "id": "msg_1", "type": "message", "role": "assistant",
                "model": "m", "stop_reason": "end_turn",
                "content": [{"type": "text", "text": MARKER}],
                "usage": {"input_tokens": 10, "output_tokens": 5},
            }
        elif "chat/completions" in path:
            provider, payload = "openai", {
                "id": "cc_1", "object": "chat.completion", "created": 0, "model": "m",
                "choices": [{"index": 0, "finish_reason": "stop",
                             "message": {"role": "assistant", "content": MARKER}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            }
        else:
            provider, payload = "gemini", {
                "candidates": [{"content": {"role": "model", "parts": [{"text": MARKER}]},
                                "finishReason": "STOP"}],
                "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5},
            }
        RECEIVED[provider] = json.dumps(body)
        data = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


server = HTTPServer(("127.0.0.1", 0), Handler)
base = f"http://127.0.0.1:{server.server_port}"
threading.Thread(target=server.serve_forever, daemon=True).start()

# A real rendered page from a real PDF — any PDF will do.
if len(sys.argv) > 1:
    pdf = Path(sys.argv[1])
else:
    pdf = next(Path(".").rglob("*.pdf"), None)
    if pdf is None:
        sys.exit("No PDF found. Pass one: python scripts/test_providers.py file.pdf")
page = P.render_pages(pdf, scale=1.0, max_edge=800)[0]
prompt = P.build_prompt(page, "Slide", use_text_layer=True)
print(f"rendered page: {len(page.png)} bytes PNG, {len(page.text_layer)} chars text layer\n")

failures = 0

# --- anthropic
try:
    import anthropic
    out = P.transcribe_anthropic(
        anthropic.Anthropic(api_key="x", base_url=base), page, "test-model", prompt)
    body = RECEIVED["anthropic"]
    assert out == MARKER, f"parse mismatch: {out!r}"
    assert '"type": "image"' in body or '"type":"image"' in body, "no image block"
    assert "base64" in body, "image not base64-encoded"
    print("anthropic  OK — request carried image, response parsed")
except Exception as e:
    failures += 1
    print(f"anthropic  FAIL — {type(e).__name__}: {e}")

# --- openai
try:
    import openai
    out = P.transcribe_openai(
        openai.OpenAI(api_key="x", base_url=base), page, "test-model", prompt)
    body = RECEIVED["openai"]
    assert out == MARKER, f"parse mismatch: {out!r}"
    assert "image_url" in body, "no image_url block"
    assert "data:image/png;base64," in body, "image not a base64 data URL"
    print("openai     OK — request carried image, response parsed")
except Exception as e:
    failures += 1
    print(f"openai     FAIL — {type(e).__name__}: {e}")

# --- gemini
try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key="x", http_options=types.HttpOptions(base_url=base))
    out = P.transcribe_gemini(client, page, "test-model", prompt)
    body = RECEIVED["gemini"]
    assert out == MARKER, f"parse mismatch: {out!r}"
    assert "inlineData" in body or "inline_data" in body, "no inline image data"
    assert "systemInstruction" in body or "system_instruction" in body, "no system prompt"
    print("gemini     OK — request carried image, response parsed")
except Exception as e:
    failures += 1
    print(f"gemini     FAIL — {type(e).__name__}: {e}")

server.shutdown()
print(f"\n{3 - failures}/3 provider paths working")
sys.exit(1 if failures else 0)
