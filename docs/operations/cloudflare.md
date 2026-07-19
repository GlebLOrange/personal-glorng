# Cloudflare Minimal Setup

Use Cloudflare as a thin edge layer in front of the production Docker Compose stack. Keep app traffic flow unchanged: Cloudflare proxies the public domain, nginx serves the SPA and proxies FastAPI, and Redis remains the app rate limiter.

## DNS

Add the zone in Cloudflare, then move the domain's authoritative nameservers to the Cloudflare nameservers.

Create these proxied records:

| Type | Name | Target | Proxy |
| --- | --- | --- | --- |
| `A` | `@` | Hetzner IPv4 | Enabled |
| `AAAA` | `@` | Hetzner IPv6, if enabled | Enabled |
| `CNAME` | `www` | root domain | Enabled |

Leave mail records DNS-only if you add email later.

## Origin TLS

Cloudflare SSL/TLS mode should be `Full (strict)`. The origin must present a valid certificate, either Let's Encrypt or a Cloudflare Origin Certificate.

For a Cloudflare Origin Certificate:

1. Create the certificate in Cloudflare: `SSL/TLS` -> `Origin Server` -> `Create Certificate`.
2. Save the certificate and key on the VPS:

   ```bash
   mkdir -p deploy/cloudflare
   chmod 700 deploy/cloudflare
   $EDITOR deploy/cloudflare/origin.pem
   $EDITOR deploy/cloudflare/origin.key
   chmod 600 deploy/cloudflare/origin.pem deploy/cloudflare/origin.key
   ```

   The `deploy/cloudflare/` directory is tracked via `.gitkeep`; `*.pem` / `*.key` stay gitignored.

3. Start production with the Cloudflare overlay:

   ```bash
   make prod-cloudflare
   ```

The overlay publishes nginx on `443` and mounts the origin cert files:

```bash
docker compose -f docker-compose.prod.yml -f docker-compose.cloudflare.yml up --build -d
```

### Origin certificate rotation

Cloudflare Origin Certificates expire (typically 15 years if you pick the max, shorter if you choose otherwise). Before expiry:

1. Create a replacement certificate in Cloudflare (`SSL/TLS` → `Origin Server`).
2. Replace `deploy/cloudflare/origin.pem` and `origin.key` on the VPS (`chmod 600`).
3. Reload nginx: `make prod-cloudflare` (or `docker compose … exec nginx nginx -s reload`).
4. Confirm `curl -I https://your-domain` still returns 200 and SSL/TLS mode stays `Full (strict)`.

## Real visitor IP

The Cloudflare overlay includes [`nginx/cloudflare_real_ip.conf`](../../nginx/cloudflare_real_ip.conf). nginx rewrites `$remote_addr` from `CF-Connecting-IP` when the peer is in Cloudflare’s published ranges, so `proxy_params.conf` still sets `X-Real-IP` to the visitor. App rate limiting ([`client_ip`](../../server/app/core/rate_limit.py)) then keys per visitor instead of per Cloudflare POP.

This include is **only** mounted for `make prod-cloudflare`. Plain `make prod` must not trust `CF-Connecting-IP`.

When Cloudflare publishes new IP ranges, update `nginx/cloudflare_real_ip.conf` (and the firewall snippet below) in a PR. Source: [cloudflare.com/ips](https://www.cloudflare.com/ips/).

### Verify

```bash
# From outside, hit a rate-limited or logged endpoint, then check app logs /
# Redis keys for your public IP (not a Cloudflare edge address).
curl -sf https://your-domain/api/health
```

## Origin allowlist (host firewall)

Compose cannot lock the VPS to Cloudflare alone. On the host, allow SSH from your admin IPs and HTTP/HTTPS only from Cloudflare ranges (same CIDRs as `cloudflare_real_ip.conf`).

Example **ufw** sketch (adjust SSH source; refresh CF CIDRs when they change):

```bash
# Allow SSH from your admin IP only
ufw allow from YOUR_ADMIN_IP to any port 22 proto tcp

# Cloudflare IPv4 → 80/443 (paste current ranges from https://www.cloudflare.com/ips-v4/)
ufw allow from 173.245.48.0/20 to any port 80,443 proto tcp
# …repeat for each IPv4/IPv6 range in cloudflare_real_ip.conf…

ufw default deny incoming
ufw enable
```

Equivalent with **nftables**: a set of Cloudflare CIDRs and accept `tcp dport { 80, 443 }` only from that set; keep an admin SSH rule.

After enabling, confirm the public hostname still works via Cloudflare proxy, and that hitting the origin IP directly on `:80`/`:443` fails from a non-CF path.

## Cache Rules

Keep caching conservative. Cache static assets only, and bypass anything dynamic or auth-related.

Recommended Cloudflare rules:

| Rule | Match | Action |
| --- | --- | --- |
| Static assets | file extension in `js css png jpg jpeg gif ico svg woff woff2 ttf webp avif` | Cache, respect origin cache headers |
| API | path starts with `/api/` | Bypass cache |
| Admin SPA | path starts with `/admin/` | Bypass cache |
| Short links | path starts with `/s/` | Bypass cache |
| File downloads | path starts with `/f/` | Bypass cache |
| Cookie traffic | request has `Cookie` header | Bypass cache |

Do not cache HTML until there is a measured need.

## Verification

After DNS has propagated:

```bash
curl -I https://example.com
curl -I https://example.com/api/health
curl -I https://example.com/assets/example.js
```

Check:

- `https://example.com` loads the SPA.
- API responses are not cached by Cloudflare.
- Static assets return the app's long-lived `Cache-Control` headers and show Cloudflare cache status after repeat requests.
- Login and logout work with secure cookies.
- Cloudflare SSL/TLS mode shows `Full (strict)`.
- Rate-limit / request logs show visitor IPs (not Cloudflare POP addresses).

## Deferred Hardening

After the minimal setup is stable, consider:

- Add small WAF or rate-limit rules only if traffic shows bot abuse.

Real visitor IP restore is in-repo (Cloudflare overlay). Origin IP allowlisting is operator-owned on the VPS (see above).

## Related

- [Deployment](/operations/deployment)
- [Security](/reference/security)
- [DevOps checklist](/operations/devops-checklist)
