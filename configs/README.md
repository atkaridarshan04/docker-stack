# Docker Stack Configurations

## Overview

This directory contains all configuration files for the Docker stack's observability and infrastructure components. Each subdirectory represents a specific service with its own configuration files and documentation.

## Configuration Structure

```
configs/
├── alloy/                    # Grafana Alloy telemetry collector
├── blackbox/                 # Blackbox Exporter for external monitoring
├── grafana/                  # Grafana dashboards and data sources
├── loki/                     # Loki log aggregation system
├── nginx/                    # NGINX reverse proxy
└── prometheus/               # Prometheus metrics collection
```

## Service Configurations

| Service | Folder |
|---------|--------|
| Grafana Alloy | [alloy](./alloy/) |
| Blackbox Exporter | [blackbox](./blackbox/) |
| Grafana | [grafana](./grafana/) |
| Loki | [loki](./loki/) |
| NGINX | [nginx](./nginx) |
| Prometheus | [prometheus](./prometheus/) |

## Data Flow Architecture

### Metrics Pipeline
```
System/Containers → Alloy → Prometheus → Grafana
                     ↓
              Blackbox Exporter
```

### Logs Pipeline
```
System/Containers → Alloy → Loki → Grafana
```

### Traffic Flow
```
External Traffic → NGINX/NPM → Flask Application
```



## Monitoring Stack Integration

### Observability Components
1. **Metrics Collection**: Alloy + Prometheus
2. **Log Aggregation**: Alloy + Loki
3. **Visualization**: Grafana dashboards
4. **External Monitoring**: Blackbox Exporter
5. **Alerting**: Prometheus rules + Grafana alerts

### Data Sources
- **System Metrics**: Node exporter functionality in Alloy
- **Container Metrics**: cAdvisor integration in Alloy
- **Application Logs**: Docker container logs via Alloy
- **System Logs**: Journal and file-based logs via Alloy
- **Health Checks**: HTTP/TCP probes via Blackbox Exporter
