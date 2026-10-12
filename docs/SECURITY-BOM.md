# Security bill of materials — relay

First relay build pending: no SBOM bundle exists yet for this repo. The table
below records the recipe inheritance from the vLLM build; versions are
confirmed at the first relay build and recorded in a dated `sbom/` bundle.

| Component | Version / source | Role | Exposure |
| --- | --- | --- | --- |
| Ubuntu Minimal 24.04 | apt, recorded per build | Guest OS, cloud-init, systemd | Broad; pruned per install recipe |
| Custom kernel 7.2.10-ntrust | `kernel/` recipe | Reduced feature set, signed modules | Boot trust path still needs provider validation |
| NVIDIA 580 open modules + userspace | pinned apt + fetches | GPU CC transport, nvattest verification | Needed for GPU profile; inert on CPU profile |
| NGINX 1.30.5 + ACME 0.4.1 | pinned hash fetch | HTTPS, TLS-ALPN-01, streaming proxy | Public parser; patch discipline applies |
| OpenSSH client/server | apt | Tunnel transport, operator admin | Restrict ingress to operator CIDR |
| Inference engine | none | Runs on developer origin, never in guest | Origin hardening is the developer's duty |

No Python engine venv ships in this image. The developer-machine client is
plain OpenSSH plus curl; those versions come from the developer's own machine
and are not part of this BOM.
