# Flask App

A message board web application built with Flask and MySQL. Users can create, edit, and delete messages. Exposes Prometheus metrics at `/metrics` and a health check at `/health`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Message board UI |
| POST | `/submit` | Create a message — body: `new_message=<text>` |
| POST | `/edit/<id>` | Update a message — body: `updated_message=<text>` |
| POST | `/delete/<id>` | Delete a message |
| GET | `/health` | Returns `{"status":"healthy"}` (200) if DB is reachable, `{"status":"unhealthy"}` (500) otherwise |
| GET | `/metrics` | Prometheus metrics |

## Metrics

`PrometheusMetrics(app)` auto-instruments all routes:

| Metric | Type | Labels |
|--------|------|--------|
| `flask_http_request_total` | Counter | `method`, `status` |
| `flask_http_request_duration_seconds` | Histogram | `method`, `path`, `status` |

Scraped by Prometheus every 15s. Visualized in the **Flask Application** Grafana dashboard.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MYSQL_HOST` | `localhost` | MySQL hostname |
| `MYSQL_USER` | `admin` | MySQL user |
| `MYSQL_DB` | `mydb` | MySQL database name |
| `MYSQL_PASSWORD_FILE` | — | Path to Docker secret file containing the DB password |
| `FLASK_DEBUG` | `0` | Always off in production |

## Secrets

The DB password is read from the Docker secret file at startup, never from a plain env var:

```python
with open(os.environ['MYSQL_PASSWORD_FILE']) as f:
    app.config['MYSQL_PASSWORD'] = f.read().strip()
```

Falls back to `MYSQL_PASSWORD` env var if the secret file is not present (local dev only).

## Build

```bash
docker compose build flask-app
docker compose up -d flask-app
```

Image: `python:3.12-slim`, non-root user `app`, served by Gunicorn (`2 workers, 4 threads, 60s timeout`).
