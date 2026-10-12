"""Verify the relay origin wiring without network access.

Runs inside the built guest with root privileges, like check-engine.py does
for the engine repos: installed unit files and the NGINX template are read
from their real paths, and the origin probe target is asserted.
"""
from pathlib import Path

unit = Path('/etc/systemd/system/ntrust-origin.service').read_text()
assert 'ExecStart=/usr/local/lib/ntrust/origin-ready' in unit
assert 'IPAddressDeny=any' in unit
assert 'IPAddressAllow=localhost' in unit

https = Path('/etc/systemd/system/ntrust-https.service').read_text()
assert 'ntrust-origin.service' in https
assert 'ntrust-inference' not in https

tee = Path('/etc/systemd/system/ntrust-tee.service').read_text()
assert 'ExecStart=/usr/local/lib/ntrust/tee-ready' in tee

template = Path('/etc/ntrust/nginx.conf.template').read_text()
assert 'proxy_pass http://127.0.0.1:8081;' in template
assert ':8080' not in template
assert 'location = /v1/models' in template
assert 'location = /v1/chat/completions' in template

probe = Path('/usr/local/lib/ntrust/origin-ready').read_text()
assert '127.0.0.1' in probe and '8081' in probe

print('PASS: relay units, NGINX template and origin probe agree on 127.0.0.1:8081.')
