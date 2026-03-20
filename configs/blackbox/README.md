# Blackbox Exporter

The Blackbox Exporter performs active probing — it makes real HTTP requests to your application and reports the result as Prometheus metrics. This is the difference between "the process is running" (liveness) and "the app actually responds correctly to HTTP" (blackbox monitoring).

## Module in Use

Only one module is configured: `http_2xx`.

```yaml
modules:
  http_2xx:
    prober: http
    timeout: 5s
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
      valid_status_codes: []   # empty = any 2xx is success
      preferred_ip_protocol: ip4
      follow_redirects: true
```

## What Gets Probed

Prometheus instructs the Blackbox Exporter to probe `http://nginx:80` using the `http_2xx` module. The probe goes through NGINX → Flask → MySQL health check, so a successful probe confirms the entire request path is working end-to-end.

## Key Metrics Produced

| Metric | Description |
|--------|-------------|
| `probe_success` | 1 = up, 0 = down |
| `probe_duration_seconds` | Total probe time |
| `probe_http_status_code` | HTTP response code |
| `probe_dns_lookup_time_seconds` | DNS resolution time |
| `probe_http_duration_seconds{phase}` | Time per phase: `connect`, `tls`, `processing`, `transfer` |

## Dashboard

The **Prometheus Blackbox Exporter** Grafana dashboard visualizes all of the above metrics with status history, response time breakdown by phase, and trend graphs.

## Adding More Probes

To probe additional URLs, add them to the `targets` list in `prometheus.yml` under the `blackbox-http` job:

```yaml
static_configs:
  - targets:
      - http://nginx:80
      - http://some-other-service:port
```

No changes to `blackbox.yml` are needed — the `http_2xx` module handles any HTTP target.
