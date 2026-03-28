# Docker Stack

<div align="center">

[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Hadolint](https://img.shields.io/badge/Hadolint-lightblue?logo=docker&logoColor=white)](https://github.com/hadolint/hadolint)
[![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![NGINX](https://img.shields.io/badge/NGINX-009639?logo=nginx&logoColor=white)](https://nginx.org/)
[![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white)](https://grafana.com/)
[![Loki](https://img.shields.io/badge/Loki-F5A623?logo=grafana&logoColor=white)](https://grafana.com/oss/loki/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*A production-style containerized application stack with full observability*

</div>

## Overview

This project is a fully containerized application stack built with production practices in mind. It runs a Flask web application backed by MySQL, served through NGINX as the sole public entry point. On top of that, a complete observability layer is wired in — Prometheus collects metrics from every service, Loki aggregates all container logs, and Grafana provides 7 pre-built dashboards covering the full stack.

## 🏗️ Architecture Overview

![Architecture](assets/architecture/project_arch-light.png)


## Dockerfile Linting

Hadolint is used to lint `app/Dockerfile` against Dockerfile best-practice rules. Configuration lives in `.hadolint.yaml` at the project root.

### Run hadolint

**Docker (no install needed):**
```bash
docker run --rm -i hadolint/hadolint < app/Dockerfile
```
![hadolint output without config](assets/hadolint-no-config.png)

**With the project config applied:**
```bash
docker run --rm -i \
  -v "$(pwd)/.hadolint.yaml:/.config/hadolint.yaml" \
  hadolint/hadolint < app/Dockerfile
```
![hadolint output with config](assets/hadolint-with-config.png)

**If hadolint is installed locally:**
```bash
hadolint --config .hadolint.yaml app/Dockerfile
```

### Ignored rule

`DL3008` — *Pin versions in apt-get install* — is intentionally ignored.

---

## Prerequisites

- Docker 20.10+ and Docker Compose v2
- Secrets files must exist before starting:

```bash
echo -n "root"  > secrets/db_root_pw.txt
echo -n "admin" > secrets/db_admin_pw.txt
```

### Start

```bash
./scripts/start.sh
```

All 10 services start in dependency order. MySQL initializes the schema on first boot (`db/init/01_schema.sql`). Flask waits for MySQL to be healthy before starting. NGINX waits for Flask.

### Stop

```bash
./scripts/stop.sh
```

Containers are removed, all named volumes (data) are preserved. To also wipe data:

```bash
docker compose down -v
```

### Rebuild the Flask image

```bash
docker compose build flask-app
docker compose up -d flask-app
```

### View logs

```bash
docker compose logs -f                  # all services
docker compose logs -f flask-app mysql  # specific services
```

### Check service status

```bash
docker compose ps
```

---

## Access

| Interface | URL | Credentials |
|-----------|-----|-------------|
| Application | http://localhost | — |
| Grafana | http://localhost:3000 | `admin` / `admin` |
| Prometheus | http://localhost:9090 | — |
| Alloy UI | http://localhost:12345 | — |
| cAdvisor | http://localhost:8080 | — |
| mysqld-exporter | http://localhost:9104/metrics | — |
| Blackbox Exporter | http://localhost:9115 | — |

---

## Observability

### Metrics

Prometheus scrapes 6 targets every 15 seconds with 15-day retention:

| Job | Source | What it measures |
|-----|--------|-----------------|
| `flask-app` | Flask `/metrics` | Request rate, latency (p50/p95/p99), error rate per endpoint |
| `cadvisor` | cAdvisor | Per-container CPU, memory, network, filesystem |
| `mysqld-exporter` | mysqld-exporter | Query throughput, connections, InnoDB buffer pool, slow queries |
| `blackbox-http` | Blackbox → NGINX | HTTP uptime, status code, response time phases |
| `blackbox-exporter` | Blackbox self | Exporter health |
| `prometheus` | Prometheus self | Scrape health, TSDB stats |

Alloy also collects host-level metrics (CPU, memory, disk, network) via its built-in node exporter and pushes them to Prometheus via remote_write.

### Logs

Alloy tails all container logs via the Docker socket and ships them to Loki with `container` and `service` labels. MySQL slow query log gets special treatment — multiline entries are reassembled and the `query_time` label is extracted for filtering.

### Dashboards

7 pre-provisioned Grafana dashboards, auto-loaded on startup:

| Dashboard | Data Source | What's inside |
|-----------|-------------|---------------|
| **Stack Overview** | Prometheus + Loki | Single-pane-of-glass — all service health, links to every other dashboard |
| **Flask Application** | Prometheus | Request rate, error rate, p50/p95/p99 latency, per-endpoint breakdown |
| **Docker Containers** | Prometheus | Per-container CPU, memory, network — links to logs |
| **MySQL** | Prometheus + Loki | Query throughput by type, connections, InnoDB, slow query log panel |
| **Container Logs** | Loki | Live log viewer, log volume, MySQL slow log, journal errors |
| **Node Exporter Full** | Prometheus | Full host system metrics |
| **Prometheus Blackbox Exporter** | Prometheus | HTTP probe status, response time breakdown by phase |

Dashboards are cross-linked — container metrics panels link directly to Container Logs filtered to that container.

---

## Secrets

Database credentials are managed via Docker Secrets — never plain environment variables.

```
secrets/
├── db_root_pw.txt    # MySQL root password
└── db_admin_pw.txt   # MySQL app user password (used by Flask + mysqld-exporter)
```

See [secrets/README.md](./secrets/README.md).

---

## Project Structure

```
docker-stack/
├── docker-compose.yml
├── .hadolint.yaml              # Hadolint Dockerfile linting config
├── app/                        # Flask application
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── templates/index.html
├── configs/                    # All service configs (mounted read-only)
│   ├── nginx/default.conf
│   ├── prometheus/prometheus.yml
│   ├── loki/loki.yml
│   ├── alloy/config.alloy
│   ├── blackbox/blackbox.yml
│   └── grafana/provisioning/
│       ├── datasources/        # Prometheus + Loki auto-wired
│       └── dashboards/json/    # 7 pre-built dashboards
├── db/init/01_schema.sql       # MySQL schema, auto-run on first start
├── secrets/                    # Never committed — gitignored
│   ├── db_root_pw.txt
│   └── db_admin_pw.txt
└── scripts/
    ├── start.sh                # docker compose up -d
    └── stop.sh                 # docker compose down (volumes preserved)
```

---

## Screenshots

### Application
![Flask Application](assets/flask-app.png)

### Prometheus Targets
![Prometheus Targets](assets/prometheus-targets.png)

### Alloy
<table>
  <tr>
    <td width="50%"><img src="assets/alloy.png" alt="Alloy Metrics" width="100%"></td>
    <td width="50%"><img src="assets/alloy-graph.png" alt="Alloy Logs" width="100%"></td>
  </tr>
</table>

### Grafana

<table>
  <tr>
    <td width="50%"><img src="assets/grafana/dashboards.png" alt="Dashboards" width="100%"></td>
    <td width="50%"><img src="assets/grafana/datasource.png" alt="Data Sources" width="100%"></td>
  </tr>
  <tr>
    <td width="50%"><img src="assets/grafana/node-dash.png" alt="Node Exporter" width="100%"></td>
    <td width="50%"><img src="assets/grafana/docker-dash.png" alt="Docker Containers" width="100%"></td>
  </tr>
  <tr>
    <td width="50%"><img src="assets/grafana/dash-blackbox-exporter.png" alt="Blackbox Exporter" width="100%"></td>
    <td width="50%"><img src="assets/grafana/app-dash.png" alt="App Dashboard" width="100%"></td>
  </tr>
  <tr>
    <td width="50%"><img src="assets/grafana/drilldown-metrics.png" alt="Metrics Drilldown" width="100%"></td>
    <td width="50%"><img src="assets/grafana/drilldown-logs.png" alt="Log Drilldown" width="100%"></td>
  </tr>
</table>
