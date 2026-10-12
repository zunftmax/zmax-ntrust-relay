# Developer-machine client

This directory holds the only code that runs on the developer-owned machine: a
small SSH reverse-tunnel opener plus this documentation. No model, prompt, or
credential is stored here by the relay design.

## Use

Start any OpenAI-compatible engine locally (vLLM, SGLang, or another harness),
then publish it at the relay's loopback listener:

```sh
./client/ntrust-tunnel -l 8000 operator@relay.example.com
```

`-l` is the local engine port. The relay always dials `127.0.0.1:8081`, so keep
the default remote port unless the relay guest was rebuilt with a different one.

Smoke-test through the relay once the tunnel is up:

```sh
curl --fail -s "https://$DOMAIN/v1/models" \
  -H "Authorization: Bearer $NTRUST_API_KEY" | head -c 400
```

## Alternatives

SSH is the default because the operator SSH channel already exists and the
direction (outbound from here) needs no inbound firewall rule on this machine.
WireGuard or stunnel with mutual TLS are acceptable substitutes: terminate the
substitute tunnel at `127.0.0.1:8081` on the relay and keep the relay guest
unchanged. Whatever transport is chosen, plaintext exists on this machine by
design, so treat this machine as inside the trust boundary.
