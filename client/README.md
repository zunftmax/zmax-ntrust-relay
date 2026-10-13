# Developer-machine client & Ntrust Python SDK

This directory holds the code that runs on the client and developer machine:
1. **Ntrust Python SDK**: The official Python client library for confidential inference.
2. **Reverse tunnel launcher (`ntrust-tunnel`)**: A minimal SSH reverse-tunnel script to connect a local engine to the relay guest.

---

## 1. Ntrust Python SDK

The SDK supports OpenAI-compatible API endpoints with hardware attestation verification, zero-leakage session binding, and zero external runtime dependencies.

### Installation

```bash
cd client
pip install .
```

### Quickstart

```python
from ntrust import ConfidentialClient

client = ConfidentialClient(
    base_url="https://inference.example.com",
    api_key="your-ram-only-api-key"
)

# Chat completion
response = client.chat.completions.create(
    model="default",
    messages=[{"role": "user", "content": "Explain confidential computing."}]
)
print(response.text)

# Streaming SSE
for chunk in client.chat.completions.stream(
    model="default",
    messages=[{"role": "user", "content": "Stream a quick summary."}]
):
    print(chunk.delta_text, end="", flush=True)
print()
```

---

## 2. Reverse Tunnel Client (`ntrust-tunnel`)

Start any OpenAI-compatible engine locally (vLLM, SGLang, or another harness), then publish it at the relay's loopback listener:

```sh
./client/ntrust-tunnel -l 8000 operator@relay.example.com
```

`-l` is the local engine port. The relay dials `127.0.0.1:8081` on its loopback interface, forwarding TLS-terminated client traffic directly through the secure tunnel to your local engine.

Smoke-test through the relay once the tunnel is up:

```sh
curl --fail -s "https://$DOMAIN/v1/models" \
  -H "Authorization: Bearer $NTRUST_API_KEY" | head -c 400
```
