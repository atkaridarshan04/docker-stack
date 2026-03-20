# Prometheus

Prometheus scrapes metrics from all services every 15 seconds and stores them with a 15-day retention window. It also receives node/system metrics pushed by Alloy via remote_write.

## Scrape Jobs

| Job | Target | Scrape interval | What it collects |
|-----|--------|-----------------|------------------|
| `prometheus` | `prometheus:9090` | 30s | Prometheus self-metrics (scrape health, TSDB stats) |
| `flask-app` | `flask-app:5000` | 15s | HTTP request rate, latency histograms, error rate per endpoint |
| `cadvisor` | `cadvisor:8080` | 15s | Per-container CPU, memory, network, filesystem |
| `mysqld-exporter` | `mysqld-exporter:9104` | 15s | MySQL queries/s, connections, InnoDB buffer pool, slow queries |
| `blackbox-http` | probes `http://nginx:80` | 15s | HTTP uptime, status code, response time breakdown |
| `blackbox-exporter` | `blackbox-exporter:9115` | 15s | Blackbox exporter self-health |

## Remote Write Receiver

Prometheus is started with `--web.enable-remote-write-receiver`, which opens the `/api/v1/write` endpoint. Alloy uses this to push node/system metrics (CPU, memory, disk, network) collected by its built-in node_exporter.

## Blackbox Probe — How It Works

The `blackbox-http` job uses relabeling to turn a list of target URLs into probe requests:

```
1. __address__ = http://nginx:80
2. relabel → __param_target = http://nginx:80  (the URL to probe)
3. relabel → instance = http://nginx:80        (for dashboard labels)
4. relabel → __address__ = blackbox-exporter:9115  (where to actually scrape)
```

Prometheus scrapes `blackbox-exporter:9115/probe?target=http://nginx:80&module=http_2xx`, and the exporter performs the actual HTTP probe and returns the result as metrics.

## Retention

15 days (`--storage.tsdb.retention.time=15d`). Data is stored in the `data_prometheus` named volume.

## Configuration File

`prometheus.yml` is mounted read-only at `/etc/prometheus/prometheus.yml`.
