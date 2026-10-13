# Developer-machine client & Ntrust Python SDK

This directory holds the code that runs on the client and developer machine:
1. **Ntrust Python SDK**: The official Python client library for confidential inference.
2. **Reverse tunnel launcher (`ntrust-tunnel`)**: A minimal SSH reverse-tunnel script to connect a local engine to the relay guest.

---

## 1. Ntrust Python SDK

The SDK supports OpenAI-compatible API endpoints with hardware attestation verification, zero-leakage session binding, and no third-party Python runtime dependencies. Attestation requires a separately installed, independently trusted Rust `uq` executable and explicit policy.

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


Attestation checks fail before connecting if the trusted binary or independent
policy is missing. The SDK no longer returns an accepting structural-only
receipt verdict. `verify_attestation=True` and `ntrust chat --attest` require
these same inputs; the CLI chat command accepts the attestation policy options.
Hardware and end-to-end acceptance remain pending; mocked adapter tests do not
establish confidential hardware compatibility.

Optional local parameters are `boot_policy`, `uki`, `google_boot_verifier` and
`prior_stage_policy` (matching CLI flags use hyphens). The Google helper must be
an absolute path to a nonempty regular executable and requires `boot_policy`.
It selects measured-boot replay, not CPU verification. Prior-stage policy is a
nonempty local JSON file bounded to 1 MiB. None of these paths or file contents
is uploaded. See [../ATTESTATION.md](../ATTESTATION.md) for runtime-log collection
and the optional companion release-pin proposal.


Attested SDK requests now perform a fresh challenge and Rust appraisal before
**every** model query, inference request, and streaming request. The SDK then
checks the actual request connection's certificate SPKI against the key observed
by the attestation transport, before sending any HTTP headers, API key, or body.
Every reconnection repeats the key check. A verified result must be used within
30 seconds; expired results and failed refreshes reject the request. A completed
response stream stays on its checked TLS connection and does not require a new
appraisal for each received chunk.

Calling `verify_attestation()` enables this requirement for subsequent requests,
even when that first check fails. `attestation_verdict` reports the latest
successful check and is never a cached authorization for later traffic. The
default mode with no attestation requested remains explicitly unverified.
Certificate-authority and hostname checks still apply. This establishes request
TLS-key continuity with the fresh attestation; it does not establish physical
CPU/GPU attachment or attest a relay's remote inference origin.
