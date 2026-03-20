# Grafana Alloy

Alloy is the telemetry agent. It runs on the host network context (with host mounts) and is responsible for:

1. Collecting host system metrics and pushing to Prometheus
2. Collecting all container logs via Docker socket and shipping to Loki
3. Tailing the MySQL slow query log and shipping to Loki with multiline parsing
4. Collecting systemd journal and system log files and shipping to Loki

## Pipeline Overview

```
Host system metrics  ──► prometheus.remote_write → Prometheus:9090
Docker container logs ──► loki.write → Loki:3100
MySQL slow query log  ──► loki.process (multiline) → loki.write → Loki:3100
systemd journal       ──► loki.write → Loki:3100
/var/log/* files      ──► loki.write → Loki:3100
```

## Sections

### System Metrics

Uses Alloy's built-in `prometheus.exporter.unix` (node_exporter equivalent). Collectors for `ipvs`, `btrfs`, `infiniband`, `xfs`, `zfs` are disabled as they are not relevant to this environment. Virtual/overlay filesystems and veth network interfaces are excluded to avoid noise from Docker internals.

Metrics are labeled with `job=node-exporter` and pushed to Prometheus via remote_write every 15 seconds.

### Docker Container Logs

Alloy connects to the Docker socket (`/var/run/docker.sock`) to discover all running containers and stream their logs. Each log entry is labeled with:

- `job=docker`
- `container=<container_name>` (extracted from `__meta_docker_container_name`)
- `service=<compose_service_name>` (extracted from the Docker Compose label)

### MySQL Slow Query Log

The slow query log is a file-based, multi-line format. Each slow query entry spans multiple lines starting with `# Time:` or `# User@Host:`. Without multiline handling, each line would be a separate Loki entry making queries unreadable.

The pipeline:
1. `loki.source.file` tails `/alloy/mysql-logs/slow.log`
2. `loki.process` with `stage.multiline` merges lines until the next `# Time:` or `# User@Host:` header — each complete query becomes one Loki entry
3. `stage.regex` extracts `Query_time` value
4. `stage.labels` promotes `query_time` to a Loki label — enabling queries like `{job="mysql-slow"} | query_time > 2`

MySQL error log is **not** tailed from file — it goes to MySQL's stderr, which Docker captures and Alloy collects automatically via the Docker logs pipeline above.

### systemd Journal

Reads from `/var/log/journal` with a 24-hour lookback. Labels each entry with `unit`, `transport`, and `level` extracted from journal metadata.

### System Log Files

Tails `/var/log/{syslog,messages,*.log}` with `job=system-logs`.

## Mounts Required

| Host path | Container path | Purpose |
|-----------|---------------|---------|
| `/` | `/rootfs` | Node exporter filesystem metrics |
| `/run` | `/run` | Runtime data |
| `/var/log` | `/var/log` | System log files + journal |
| `/sys` | `/sys` | Kernel/hardware metrics |
| `/var/lib/docker` | `/var/lib/docker` | Docker metadata |
| `/run/udev/data` | `/run/udev/data` | Hardware device info |
| `/var/run/docker.sock` | `/var/run/docker.sock` | Docker API for log collection |
| `mysql-logs` volume | `/alloy/mysql-logs` | MySQL slow query log |
