# Grafana Alloy Configuration

## Overview

**Grafana Alloy** is a vendor-neutral distribution of the OpenTelemetry (OTel) Collector. It's a telemetry collector that can ingest, transform, and forward telemetry data (metrics, logs, traces) to multiple destinations. In this setup, Alloy acts as a unified data collection agent that gathers system metrics, container metrics, and logs from various sources.

## Role in Current Setup

Alloy serves as the central telemetry collection hub that:
- **Collects system metrics** using built-in node exporter functionality
- **Gathers Docker container metrics** via cAdvisor integration
- **Aggregates logs** from system files, Docker containers, and MySQL
- **Forwards data** to Prometheus (metrics) and Loki (logs)
- **Provides unified observability** across the entire stack

## Configuration Structure

The `config.alloy` file is organized into several sections:

### 1. Data Destinations (TARGETS)

```alloy
// Loki endpoint for log forwarding
loki.write "default" {
    endpoint {
        url = "http://loki:3100/loki/api/v1/push"  // Internal Docker network URL
    }
    external_labels = {}  // Additional labels for all logs
}

// Prometheus endpoint for metrics forwarding
prometheus.remote_write "default" {
    endpoint {
        url = "http://prometheus:9090/api/v1/write"  // Remote write API endpoint
    }
}
```

### 2. System Logs & Journal Collection

```alloy
// Systemd journal log collection
loki.source.journal "journal" {
    max_age       = "24h0m0s"           // Collect logs from last 24 hours
    relabel_rules = discovery.relabel.journal.rules  // Apply labeling rules
    forward_to    = [loki.write.default.receiver]    // Send to Loki
    labels        = {component = string.format("%s-journal", constants.hostname)}
    path          = "/var/log/journal"   // Journal directory path
}

// System log files collection
local.file_match "system" {
    path_targets = [{
        __address__ = "localhost",
        __path__    = "/var/log/{syslog,messages,*.log}",  // Log file patterns
        instance    = constants.hostname,
        job         = string.format("%s-logs", constants.hostname),
    }]
}
```

### 3. System Metrics Collection

```alloy
// Node exporter for system metrics
prometheus.exporter.unix "metrics" {
    disable_collectors = ["ipvs", "btrfs", "infiniband", "xfs", "zfs"]  // Unused collectors
    enable_collectors = ["meminfo"]  // Additional memory info
    filesystem {
        fs_types_exclude     = "^(autofs|binfmt_misc|bpf|cgroup2?|...)$"  // Exclude virtual filesystems
        mount_points_exclude = "^/(dev|proc|run/credentials/.+|...)$"      // Exclude system mounts
        mount_timeout        = "5s"  // Filesystem mount timeout
    }
    netclass {
        ignored_devices = "^(veth.*|cali.*|[a-f0-9]{15})$"  // Ignore virtual network devices
    }
}

// Scrape system metrics every 15 seconds
prometheus.scrape "metrics" {
    scrape_interval = "15s"
    targets    = discovery.relabel.metrics.output
    forward_to = [prometheus.remote_write.default.receiver]
}
```

### 4. Docker Container Metrics

```alloy
// cAdvisor for container metrics
prometheus.exporter.cadvisor "dockermetrics" {
    docker_host = "unix:///var/run/docker.sock"  // Docker socket connection
    storage_duration = "5m"  // Metric retention in memory
}

// Scrape container metrics every 10 seconds
prometheus.scrape "dockermetrics" {
    targets    = prometheus.exporter.cadvisor.dockermetrics.targets
    forward_to = [prometheus.remote_write.default.receiver]
    scrape_interval = "10s"
}
```

### 5. Docker Container Logs

```alloy
// Discover running Docker containers
discovery.docker "dockerlogs" {
    host = "unix:///var/run/docker.sock"
}

// Relabel container metadata
discovery.relabel "dockerlogs" {
    rule {
        source_labels = ["__meta_docker_container_name"]
        regex = "/(.*)"           // Remove leading slash from container name
        target_label = "service_name"
    }
}

// Collect logs from all Docker containers
loki.source.docker "default" {
    host       = "unix:///var/run/docker.sock"
    targets    = discovery.docker.dockerlogs.targets
    labels     = {"platform" = "docker"}  // Add platform label
    relabel_rules = discovery.relabel.dockerlogs.rules
    forward_to = [loki.write.default.receiver]
}
```

### 6. MySQL Specific Logs

```alloy
// MySQL log files collection
local.file_match "mysql" {
    path_targets = [{
        __address__ = "localhost",
        __path__    = "/logs/mysql/*.log",  // MySQL log directory (mounted volume)
        instance    = constants.hostname,
        job         = "mysql",
    }]
}

loki.source.file "mysql" {
    targets    = local.file_match.mysql.targets
    forward_to = [loki.write.default.receiver]
}
```

## Key Features

### Data Collection
- **System Metrics**: CPU, memory, disk, network statistics
- **Container Metrics**: Resource usage, performance metrics for all containers
- **System Logs**: Syslog, journal entries, application logs
- **Container Logs**: Stdout/stderr from all Docker containers
- **MySQL Logs**: Error logs, slow query logs, binary logs

### Data Processing
- **Label Management**: Automatic labeling with hostname, service names
- **Filtering**: Excludes virtual filesystems and network devices
- **Relabeling**: Transforms metadata into meaningful labels
- **Routing**: Sends metrics to Prometheus, logs to Loki

### Performance Optimization
- **Selective Collection**: Disables unnecessary collectors
- **Efficient Scraping**: Different intervals for different data types
- **Memory Management**: Configurable storage duration for metrics

## Volume Mounts

The Alloy container requires several volume mounts for data collection:

```yaml
volumes:
  - ./configs/alloy/config.alloy:/etc/alloy/config.alloy  # Configuration file
  - alloy_data:/var/lib/alloy/data                       # Alloy data storage
  - /:/rootfs:ro                                         # Host filesystem (read-only)
  - /run:/run:ro                                         # Runtime information
  - /var/log:/var/log:ro                                 # System logs
  - /sys:/sys:ro                                         # System information
  - /var/lib/docker/:/var/lib/docker/:ro                 # Docker data
  - /run/udev/data:/run/udev/data:ro                     # Device information
  - ./app/mysql/logs:/log/mysql:ro                       # MySQL logs
```

## Network Configuration

- **Port**: 12345 (Web UI and API)
- **Network**: app-net (internal Docker network)
- **Dependencies**: None (runs independently)

## Monitoring Capabilities

### What Alloy Monitors
1. **Host System**: CPU, memory, disk I/O, network traffic
2. **Docker Containers**: Resource usage, restart counts, health status
3. **Application Logs**: All container stdout/stderr output
4. **System Logs**: Kernel messages, service logs, authentication logs
5. **MySQL Database**: Query logs, error logs, performance metrics

### Data Flow
```
Host System → Alloy → Prometheus (metrics)
                ↓
            Loki (logs)
```
