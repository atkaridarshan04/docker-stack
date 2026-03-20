# Configs

All service configuration files. Each subdirectory maps 1:1 to a service in `docker-compose.yml` and is mounted read-only into the container.

| Directory | Service | Mounted at |
|-----------|---------|------------|
| `nginx/` | nginx-proxy | `/etc/nginx/conf.d/default.conf` |
| `prometheus/` | prometheus | `/etc/prometheus/` |
| `loki/` | loki | `/etc/loki/config.yaml` |
| `alloy/` | alloy | `/etc/alloy/config.alloy` |
| `blackbox/` | blackbox-exporter | `/etc/blackbox_exporter/config.yml` |
| `grafana/provisioning/` | grafana | `/etc/grafana/provisioning/` |

Grafana datasources and dashboards are provisioned automatically from `grafana/provisioning/` — no manual setup needed.
