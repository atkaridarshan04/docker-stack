# Grafana

Grafana is the visualization layer. It reads from both Prometheus (metrics) and Loki (logs) and serves pre-built dashboards that are provisioned automatically on startup — no manual import or configuration needed.

## Access

`http://localhost:3000` — default credentials: `admin` / `admin`

## Provisioning

Everything under `provisioning/` is mounted into the container at `/etc/grafana/provisioning/` and loaded automatically when Grafana starts.

```
provisioning/
├── datasources/
│   └── datasources.yml     # Prometheus + Loki connections
└── dashboards/
    ├── dashboards.yml       # Tells Grafana where to find dashboard JSON files
    └── json/                # Dashboard JSON files — one file per dashboard
```

### Datasources (`datasources/datasources.yml`)

| Name | Type | URL | UID |
|------|------|-----|-----|
| Prometheus | prometheus | `http://prometheus:9090` | `PBFA97CFB590B2093` |
| Loki | loki | `http://loki:3100` | `P8E80F9AEF21F6940` |

UIDs are hardcoded so dashboard JSON files can reference them reliably without depending on auto-generated IDs.

### Dashboard Provider (`dashboards/dashboards.yml`)

Watches `/etc/grafana/provisioning/dashboards/json/` and loads all `.json` files as dashboards. `updateIntervalSeconds: 30` means changes to JSON files are picked up within 30 seconds without restarting Grafana.

## Dashboards

All dashboards use modern Grafana panel types (`timeseries`, `stat`, `logs`, `table`). No deprecated `graph` or `singlestat` panels.

| File | Dashboard | Data Source | Description |
|------|-----------|-------------|-------------|
| `overview.json` | Stack Overview | Prometheus + Loki | Single-pane-of-glass across all services. Rows for App, Infrastructure, Database, Logs. Each section links to the detailed dashboard. |
| `flask_app.json` | Flask Application | Prometheus | Request rate, error rate, p50/p95/p99 latency, per-endpoint breakdown, uptime status. Panels link to Container Logs filtered to `flask-app`. |
| `docker_containers.json` | Docker Containers | Prometheus | Per-container CPU %, memory working set, network in/out, resource summary table. Panels link to Container Logs filtered to the clicked container. |
| `mysql.json` | MySQL | Prometheus + Loki | Query throughput by type (SELECT/INSERT/UPDATE/DELETE), connections vs max, InnoDB buffer pool breakdown, network traffic, slow query log panel. |
| `loki_logs.json` | Container Logs | Loki | Log volume by container (stacked bars), live container log viewer (filterable by container), MySQL slow query log, system journal errors. |
| `1860_rev42.json` | Node Exporter Full | Prometheus | Full host system metrics — CPU, memory, disk, network, filesystem, processes. |
| `blackbox_exporter.json` | Prometheus Blackbox Exporter | Prometheus | HTTP probe status, response time breakdown by phase (connect/processing/transfer), probe success history. |

### Cross-Dashboard Links

Dashboards are linked so you can drill from metrics to logs without losing context:

- **Docker Containers** → click any container series → jumps to Container Logs filtered to that container
- **Flask Application** panels → "View Flask Logs" → Container Logs filtered to `flask-app`
- **MySQL** panels → "View MySQL Error Logs" → Container Logs filtered to `mysql`
- **Stack Overview** each section → links to the detailed dashboard for that service

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GF_SECURITY_ADMIN_PASSWORD` | `admin` | Grafana admin password |
| `GF_ANALYTICS_REPORTING_ENABLED` | `false` | Disable telemetry to Grafana Labs |
| `GF_ANALYTICS_CHECK_FOR_UPDATES` | `false` | Disable update checks |
| `GF_LOG_LEVEL` | `warn` | Reduce log verbosity |

## Adding a New Dashboard

1. Build or export the dashboard JSON from Grafana UI
2. Ensure all datasource references use the hardcoded UIDs (`PBFA97CFB590B2093` for Prometheus, `P8E80F9AEF21F6940` for Loki)
3. Set `"id": null` and assign a unique `"uid"` string
4. Drop the file into `configs/grafana/provisioning/dashboards/json/`
5. Grafana picks it up within 30 seconds — no restart needed
