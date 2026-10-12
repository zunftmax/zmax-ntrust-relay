# Zmax ntrust · relay

Zmax is proud to support and open source these reference images for trusted and confidential inference and token streaming. This repository is the harness-free relay image in the ntrust family. The guest terminates public HTTPS with
a Let's Encrypt certificate obtained in-guest via TLS-ALPN-01, then forwards
`GET /v1/models` and `POST /v1/chat/completions` to a developer-owned origin
(vLLM, SGLang, or any OpenAI-compatible engine) behind an encrypted tunnel.
No inference engine, model weight, prompt log, or telemetry service runs in
this image.

**Status:** experimental skeleton derived from the vLLM recipe. No cloud run
has been validated yet. Customer verification of the image and TLS identity is
deferred. Do not interpret a successful local build as a confidential-computing
proof.

The sibling projects are [zmax-ntrust-vllm](https://github.com/ZUNFTMAX/zmax-ntrust-vllm),
[zmax-ntrust-sglang](https://github.com/ZUNFTMAX/zmax-ntrust-sglang), and the
CPU tryout image `zmax-ntrust-dev`.

## What runs

```text
Client ── TLS 1.3 / JSON or SSE ── cloud TCP forwarding ── guest NGINX :443
                                                           │ loopback
                                              tunnel listener 127.0.0.1:8081
                                                           │ encrypted tunnel
                                              developer machine engine :8000
```

NGINX proxies to the tunnel listener only. The developer machine dials outbound
with [client/ntrust-tunnel](client/ntrust-tunnel), so no inbound firewall rule
is needed on the developer side. Responses return over the client's existing
HTTPS connection; streaming uses SSE. Keep any load balancer at layer 4 so TLS
terminates in the guest.

The guest requires SEV-SNP or TDX, disabled swap, and a live origin tunnel
before serving. When a CC-capable NVIDIA GPU (H100, H200, B100, B200) is
attached in production CC-On mode, the gate runs full local NVIDIA verification
first; without a GPU the gate logs the CPU relay path and continues. NVIDIA
supplies GPU attestation, SPDM and link encryption. The project adds no thread
pool, spinlock or GPU encryption implementation.

## Privacy and key lifecycle

- TLS/ACME state and the API credential stay in RAM. Swap, core dumps,
  suspend, hibernation and pstore are disabled.
- A full HTTPS restart deliberately creates a new TLS key and certificate.
  Reload retains the running ACME state. Reboot creates a new API credential.
  Use ACME staging while testing repeated restarts.
- Plaintext requests exist inside TEE RAM and on the trusted developer
  machine by design. The tunnel between them is encrypted; the cloud observes
  traffic metadata, allocation and availability only.
- No prompt/response logging or telemetry service is configured. Upstream
  logging outputs are discarded. The root disk holds software only.
- Cloud metadata contains only public bootstrap configuration.

These controls do not yet let a customer authenticate the running image.
Certificate Transparency records issuance, not image approval. See
[security boundaries](docs/SECURITY-REVIEW.md) and the [remote verification
next phase](docs/REMOTE-ATTESTATION.md).

## Build on Linux

Use an x86-64 Linux host with KVM, Packer 1.16.1, QEMU 8.2.2 or compatible
tools, OVMF 4M, xorriso, Python 3, gettext and ShellCheck. The [minimal kernel
build](kernel/README.md) also needs GCC/G++, make, bc, bison, flex,
libssl-dev, libelf-dev, GnuPG and dpkg tools. Image builds for this project
run on `axp.computer` over SSH. Do not emulate the image on macOS.

```sh
make check
make image
make export
bash tests/smoke-guest.sh
bash tests/inspect-image.sh
make sbom
sha256sum --check dist/SHA256SUMS
```

Outputs are `dist/qemu/ntrust.qcow2`, `dist/ntrust-azure.vhd`,
`dist/ntrust-gcp.tar.gz` and `dist/SHA256SUMS`. Build/SSH keys and disk files
are ignored by Git. The ordinary KVM smoke test must refuse to serve without
the tunnel; it cannot exercise confidential execution.

Base package versions are recorded from each build. Ubuntu packages are not
snapshot-pinned, so reproducible releases are not claimed.

## Deploy

Launch on a CPU confidential VM for tryout, or attach a CC-capable NVIDIA GPU
for the GPU relay profile. Follow the separate [Azure and GCP launch
recipes](image/clouds.md). Obtain a DNS hostname, an operator SSH public key
and TCP 443 pass-through. Copy `guest/cloud-init.example.yaml`, replace the
public placeholders and use the staging CA first. Then open the tunnel from
the developer machine (see [client/](client/README.md)) and confirm
`sudo ntrust-status` reports `origin: ready`.

## Run

Retrieve `/run/ntrust-tee/api-key` using your trusted operator SSH channel and
place it in your client's secret storage. Do not send it through cloud
metadata or application logs.

```sh
# NTRUST_API_KEY is the per-boot credential; DOMAIN is your provisioned hostname.
curl --fail --no-buffer "https://$DOMAIN/v1/chat/completions" \
  -H "Authorization: Bearer $NTRUST_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"model","messages":[{"role":"user","content":"Reply with hello."}],"max_tokens":16,"stream":true}'
```

Use `sudo ntrust-status` for payload-free local diagnostics. Full HTTPS
restarts reissue certificates; use staging during diagnosis to avoid
production issuance limits.

## Project contents

| Path | Purpose |
| --- | --- |
| `guest/` | TEE gate, origin wait, upstream proxy configuration and service isolation |
| `client/` | Developer-machine tunnel opener and its documentation |
| `kernel/` | Linux 7.2.10 feature allowlist, signed headless NVIDIA modules and build recipe |
| `image/` | Packer recipe, disk export, origin-wiring check and provider launch instructions |
| `tests/` | Admission/credential tests, ordinary UEFI boot checks and artifact inspection |
| `docs/SECURITY-REVIEW.md` | Boundaries of the relay: what the TEE covers and what it does not |
| `docs/REMOTE-ATTESTATION.md` | Reserved follow-on scope for customer verification and sealing |

Project code uses the MIT license. NVIDIA components, NGINX and Ubuntu retain
their own licenses. Installed license files and package metadata are retained
in the image.
