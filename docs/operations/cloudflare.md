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

3. Start production with the Cloudflare overlay:

   ```bash
   make prod-cloudflare
   ```

The overlay publishes nginx on `443` and mounts the origin cert files:

```bash
docker compose -f docker-compose.prod.yml -f docker-compose.cloudflare.yml up --build -d
```

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

## Deferred Hardening

After the minimal setup is stable, consider a separate hardening pass:

- Restore real visitor IPs from Cloudflare headers before app rate limiting decisions.
- Restrict direct origin traffic to Cloudflare IP ranges in the VPS firewall.
- Add small WAF or rate-limit rules only if traffic shows bot abuse.

## Related

- [Deployment](/operations/deployment)
- [Security](/reference/security)
