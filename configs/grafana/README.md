# Grafana Configuration

## Overview

**Grafana** is an open-source analytics and interactive visualization web application. It provides charts, graphs, and alerts when connected to supported data sources. In this setup, Grafana serves as the primary visualization and dashboarding platform for monitoring the entire Docker stack.

## Role in Current Setup

Grafana acts as the central monitoring dashboard that:
- **Visualizes metrics** from Prometheus (system, container, and application metrics)
- **Displays logs** from Loki (system, container, and application logs)
- **Provides pre-configured dashboards** for comprehensive monitoring
- **Enables alerting** based on metrics and log patterns
- **Offers unified observability** across the entire infrastructure

## Configuration Structure

The Grafana configuration uses provisioning to automatically set up data sources and dashboards:

```
configs/grafana/provisioning/
├── datasources/
│   └── datasources.yml          # Data source configurations
└── dashboards/
    ├── dashboards.yml           # Dashboard provider configuration
    ├── 1860_rev42.json         # Node Exporter Dashboard
    ├── 193_rev1.json           # Docker Container Dashboard
    ├── 7587_rev3.json          # MySQL Dashboard
    └── 13639_rev2.json         # Blackbox Exporter Dashboard
```

## Data Sources Configuration

### datasources.yml

```yaml
apiVersion: 1

datasources:
  # Prometheus data source for metrics
  - name: Prometheus
    type: prometheus
    access: proxy                    # Access through Grafana backend
    url: http://prometheus:9090      # Internal Docker network URL
    uid: PBFA97CFB590B2093          # Unique identifier
    isDefault: true                  # Default data source for new panels
    editable: true                   # Allow editing in UI

  # Loki data source for logs
  - name: Loki
    type: loki
    access: proxy                    # Access through Grafana backend
    url: http://loki:3100           # Internal Docker network URL
    uid: P8E80F9AEF21F6940          # Unique identifier
    editable: true                   # Allow editing in UI
```

**Key Features:**
- **Automatic provisioning**: Data sources are configured on startup
- **Proxy access**: Requests go through Grafana server (secure)
- **Internal networking**: Uses Docker service names for connectivity
- **Editable**: Can be modified through Grafana UI

## Dashboard Provisioning

### dashboards.yml

```yaml
apiVersion: 1

providers:
  - name: 'default'                    # Provider name
    orgId: 1                          # Organization ID (default org)
    folder: ''                        # Root folder (no subfolder)
    type: file                        # File-based provisioning
    disableDeletion: false            # Allow dashboard deletion
    updateIntervalSeconds: 10         # Check for updates every 10 seconds
    allowUiUpdates: true              # Allow UI modifications
    options:
      path: /etc/grafana/provisioning/dashboards  # Dashboard files location
```

**Configuration Details:**
- **Automatic loading**: Dashboards are imported on startup
- **File watching**: Updates dashboards when files change
- **UI integration**: Allows modifications through Grafana interface
- **Version control**: Dashboard JSON files can be version controlled

## Pre-configured Dashboards

### 1. Node Exporter Dashboard (ID: 1860)
**File**: `1860_rev42.json`

**Purpose**: System-level monitoring
- **CPU Usage**: Utilization, load average, context switches
- **Memory**: Usage, available, swap utilization
- **Disk I/O**: Read/write operations, disk space usage
- **Network**: Traffic, packet rates, error rates
- **System**: Uptime, file descriptor usage, processes

**Key Metrics:**
- `node_cpu_seconds_total`
- `node_memory_MemAvailable_bytes`
- `node_disk_io_time_seconds_total`
- `node_network_receive_bytes_total`

### 2. Docker Container Dashboard (ID: 193)
**File**: `193_rev1.json`

**Purpose**: Container resource monitoring
- **Container CPU**: Usage per container, throttling
- **Container Memory**: Usage, limits, cache
- **Container Network**: Traffic per container
- **Container Filesystem**: Disk usage per container
- **Container Status**: Running, stopped, restart counts

**Key Metrics:**
- `container_cpu_usage_seconds_total`
- `container_memory_usage_bytes`
- `container_network_receive_bytes_total`
- `container_fs_usage_bytes`

### 3. MySQL Dashboard (ID: 7587)
**File**: `7587_rev3.json`

**Purpose**: Database performance monitoring
- **Connection Metrics**: Active connections, connection rate
- **Query Performance**: Query rate, slow queries, execution time
- **InnoDB Metrics**: Buffer pool usage, row operations
- **Replication**: Master/slave status, lag
- **Table Locks**: Lock waits, lock time

**Key Metrics:**
- `mysql_global_status_connections`
- `mysql_global_status_queries`
- `mysql_global_status_slow_queries`
- `mysql_global_status_innodb_buffer_pool_pages_total`

### 4. Blackbox Exporter Dashboard (ID: 13639)
**File**: `13639_rev2.json`

**Purpose**: External service monitoring
- **Probe Success Rate**: Service availability over time
- **Response Time**: HTTP response times, DNS lookup time
- **SSL Certificate**: Certificate expiry monitoring
- **HTTP Status Codes**: Distribution of response codes
- **Probe Duration**: Time taken for different probe types

**Key Metrics:**
- `probe_success`
- `probe_duration_seconds`
- `probe_http_status_code`
- `probe_ssl_earliest_cert_expiry`

## Volume Mounts

```yaml
volumes:
  - grafana-data:/var/lib/grafana                           # Persistent data storage
  - ./configs/grafana/provisioning:/etc/grafana/provisioning # Configuration provisioning
```

**Mount Details:**
- **grafana-data**: Stores dashboards, users, settings, and other persistent data
- **provisioning**: Contains data source and dashboard configurations

## Network Configuration

- **Port**: 3000 (Web UI)
- **Network**: app-net (internal Docker network)
- **Dependencies**: Loki, Prometheus (for data sources)
- **Access**: http://localhost:3000

## Default Credentials

- **Username**: admin
- **Password**: admin (should be changed on first login)

## Key Features

### Visualization Capabilities
1. **Time Series Graphs**: CPU, memory, network metrics over time
2. **Heatmaps**: Performance distribution analysis
3. **Tables**: Detailed metric breakdowns
4. **Stat Panels**: Current values and trends
5. **Logs Panel**: Real-time log streaming and search

### Alerting Features
1. **Metric-based Alerts**: CPU, memory, disk thresholds
2. **Log-based Alerts**: Error pattern detection
3. **Multi-channel Notifications**: Email, Slack, webhook
4. **Alert Rules**: Complex conditions and expressions

### Data Exploration
1. **Query Builder**: Visual query construction
2. **Explore Mode**: Ad-hoc data investigation
3. **Log Correlation**: Link metrics to related logs
4. **Variable Templates**: Dynamic dashboard filtering
