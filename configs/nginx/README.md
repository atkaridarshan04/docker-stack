# NGINX

NGINX acts as the sole public entry point for the application. All user traffic hits NGINX on port 80, which proxies it to the Flask app internally. The Flask container has no host port binding — it is unreachable except through NGINX.

## Configuration: `default.conf`

### Upstream block

```nginx
upstream flask {
    server flask-app:5000;
    keepalive 32;
}
```

Defines a named upstream group pointing to the Flask container. `keepalive 32` maintains a pool of 32 persistent connections to Flask, avoiding TCP handshake overhead on every request.

### Proxy headers

```nginx
proxy_http_version 1.1;
proxy_set_header Connection "";
proxy_set_header Host              $host;
proxy_set_header X-Real-IP         $remote_addr;
proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

- `proxy_http_version 1.1` + `Connection ""` — required for keepalive connections to upstream
- `X-Real-IP` / `X-Forwarded-For` — passes the real client IP to Flask for logging
- `X-Forwarded-Proto` — tells Flask whether the original request was HTTP or HTTPS

### Timeouts

```nginx
proxy_connect_timeout 5s;
proxy_read_timeout    60s;
proxy_send_timeout    60s;
```

5s to establish connection to Flask. 60s for read/write — accommodates slow DB queries without dropping the connection.

### Gzip

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

Compresses text responses before sending to the client. Reduces bandwidth for JSON API responses and static assets.

### Locations

| Location | Behaviour |
|----------|-----------|
| `/` | Proxy all requests to Flask |
| `/health` | Proxy to Flask `/health`, access log suppressed (avoids polluting logs with healthcheck noise) |

## Health Check

The NGINX container healthcheck calls `curl -sf http://localhost/health`, which proxies through to Flask's `/health` endpoint. This means NGINX is only considered healthy when Flask is also healthy and responding correctly.
