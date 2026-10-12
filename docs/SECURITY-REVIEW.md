# Security review — relay

Harness-free relay: NGINX terminates public TLS in the guest and forwards two
OpenAI-compatible routes to the developer-owned origin at `127.0.0.1:8081`.
No inference engine or model weight exists in this image.

## What the TEE covers

- Public TLS terminates inside the SEV-SNP/TDX guest; the Let's Encrypt key is
  generated in guest RAM via TLS-ALPN-01.
- The per-boot API credential is minted only after the TEE gate passes and is
  never written to disk.
- NGINX exposes exactly `GET /v1/models` and `POST /v1/chat/completions`;
  every other route returns 404, and access/error logging is disabled.
- `ntrust-origin` talks only to loopback; the tunnel listener is the only
  permitted upstream.

## What the TEE does not cover

- Plaintext requests exist on the developer-owned origin machine by design.
  Treat that machine as inside the trust boundary.
- The encrypted tunnel hides content but not timing, sizes, or availability
  from the network and the cloud provider.
- With no GPU attached, the CPU relay path performs no GPU verification.
  Never present a CPU relay boot as confidential GPU evidence.
- Customer verification of the image and TLS identity is deferred to the
  remote-attestation phase.

## Remaining hardware checks

Cloud import, live ACME issuance, tunnel bring-up against a real origin, GPU
CC-On verification on each supported SKU (H100, H200, B100, B200), and
reboot/key-rotation behavior all require hardware runs. The ordinary KVM smoke
test refuses to serve without the tunnel; refusal is not a proof of
confidential execution.
