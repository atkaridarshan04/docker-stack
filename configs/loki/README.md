# Loki

Loki is the log aggregation backend. Alloy ships all logs to Loki, and Grafana queries Loki for log dashboards and exploration.

## Configuration

Single-binary mode with in-memory ring (no distributed coordination needed for a single-node setup).

### Storage

Filesystem storage — chunks and index stored in the `data_loki` named volume at `/loki`.

```
/loki/chunks/   — compressed log chunks
/loki/rules/    — alerting rules (unused currently)
/loki/compactor/ — compactor working directory
```

### Schema

TSDB store with schema v13 (current recommended schema). Index period of 24h.

### Retention

```yaml
limits_config:
  retention_period: 30d

compactor:
  retention_enabled: true
```

Logs older than 30 days are automatically deleted by the compactor. The compactor runs as part of the single-binary and handles both compaction and retention enforcement.

### Query Cache

Embedded in-memory cache (100MB) for query range results — speeds up repeated dashboard queries over the same time range.

### Pattern Ingester

Enabled for automatic log pattern detection and metric aggregation from log volume. Useful for the log volume panels in Grafana dashboards.

## Loki Labels in Use

| Label | Values | Source |
|-------|--------|--------|
| `job` | `docker`, `mysql-slow`, `systemd-journal`, `system-logs` | Set by Alloy pipeline |
| `container` | `flask-app`, `mysql`, `nginx-proxy`, etc. | Extracted from Docker container name |
| `service` | `flask-app`, `mysql`, `nginx`, etc. | Extracted from Docker Compose service label |
| `unit` | systemd unit names | Extracted from journal |
| `transport` | `journal`, `stdout`, etc. | Extracted from journal |
| `level` | `info`, `warning`, `error`, etc. | Extracted from journal priority |
| `query_time` | float string | Extracted from MySQL slow query log |

## Querying

Access Loki directly at `http://localhost:3100` or through Grafana's Explore view (select Loki datasource).

Example LogQL queries:

```logql
# All logs from a specific container
{job="docker", container="flask-app"}

# MySQL slow queries taking more than 2 seconds
{job="mysql-slow"} | query_time > 2

# Errors across all containers
{job="docker"} |~ "(?i)(error|exception|fatal)"

# systemd journal errors
{job="systemd-journal"} | level="error"
```
