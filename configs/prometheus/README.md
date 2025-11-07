# Prometheus Configuration

## Overview

**Prometheus** is an open-source systems monitoring and alerting toolkit. It collects and stores metrics as time series data, providing powerful querying capabilities through PromQL (Prometheus Query Language). In this setup, Prometheus serves as the central metrics collection and storage system for monitoring the entire Docker stack.

## Role in Current Setup

Prometheus acts as the metrics hub that:
- **Collects metrics** from various sources (Alloy, Blackbox Exporter)
- **Stores time-series data** with efficient compression and retention
- **Provides PromQL interface** for querying and analysis
- **Serves as data source** for Grafana dashboards
<!-- - **Enables alerting** based on metric thresholds and patterns
- **Offers service discovery** for dynamic target management -->

## Configuration Structure

The `prometheus.yml` file defines the global settings and scrape configurations:

### 1. Global Configuration

```yaml
global:
  scrape_interval: 15s  # Default interval for scraping targets
```

**Purpose**: Sets the default scraping frequency for all jobs. This can be overridden per job for different collection requirements.

### 2. Scrape Configurations

The scrape_configs section defines what targets to monitor and how to collect metrics from them.

#### Self-Monitoring Job

```yaml
- job_name: 'prometheus'
  scrape_interval: 5s              # More frequent scraping for self-monitoring
  static_configs:
    - targets: ['localhost:9090']  # Prometheus monitoring itself
```

**Metrics Collected**:
- `prometheus_tsdb_head_samples_appended_total` - Ingestion rate
- `prometheus_tsdb_head_series` - Number of active time series
- `prometheus_config_last_reload_successful` - Configuration reload status
- `prometheus_rule_evaluation_duration_seconds` - Rule evaluation performance

#### Blackbox Probing Job

```yaml
- job_name: "blackbox"
  metrics_path: /probe              # Blackbox exporter probe endpoint
  params:
    module: [http_2xx]             # Use http_2xx probe module
  static_configs:
    - targets:
        - http://nginx:80          # Target to probe
        # Additional targets for NGINX Proxy Manager setup:
        # - https://npm.deployzone.duckdns.org
        # - https://app.deployzone.duckdns.org
        # - https://grafana.deployzone.duckdns.org
        # - https://prometheus.deployzone.duckdns.org
        # - https://alloy.deployzone.duckdns.org
        # - https://blackbox-exporter.deployzone.duckdns.org
```

**Relabeling Configuration**:
```yaml
relabel_configs:
  - source_labels: [__address__]
    target_label: __param_target    # Set probe target parameter
  - source_labels: [__param_target]
    target_label: instance          # Set instance label
  - target_label: __address__
    replacement: blackbox-exporter:9115  # Redirect to blackbox exporter
```

**Purpose**: 
- **External monitoring**: Tests service availability from outside
- **Health validation**: Ensures services respond correctly to HTTP requests
- **Performance tracking**: Measures response times and success rates

#### Blackbox Exporter Metrics

```yaml
- job_name: "blackbox_exporter"
  static_configs:
    - targets: ["blackbox-exporter:9115"]  # Blackbox exporter's own metrics
```

**Metrics Collected**:
- `blackbox_exporter_config_last_reload_successful` - Configuration status
- `prometheus_sd_discovered_targets` - Service discovery targets
- Internal performance and operational metrics

## Data Sources Integration

### Alloy Remote Write

Prometheus receives metrics from Alloy via remote write API:

```yaml
# Alloy configuration (in config.alloy)
prometheus.remote_write "default" {
  endpoint {
    url = "http://prometheus:9090/api/v1/write"
  }
}
```

**Metrics Received from Alloy**:
- **System metrics**: CPU, memory, disk, network from node exporter
- **Container metrics**: Docker container resource usage from cAdvisor
- **Custom metrics**: Application-specific metrics from Flask app

<!-- ## Metrics Collection Overview

### 1. System Metrics (via Alloy)
```promql
# CPU usage
node_cpu_seconds_total

# Memory usage
node_memory_MemAvailable_bytes
node_memory_MemTotal_bytes

# Disk I/O
node_disk_read_bytes_total
node_disk_written_bytes_total

# Network traffic
node_network_receive_bytes_total
node_network_transmit_bytes_total
```

### 2. Container Metrics (via Alloy)
```promql
# Container CPU usage
container_cpu_usage_seconds_total

# Container memory usage
container_memory_usage_bytes
container_memory_limit_bytes

# Container network
container_network_receive_bytes_total
container_network_transmit_bytes_total

# Container filesystem
container_fs_usage_bytes
container_fs_limit_bytes
```

### 3. Application Health (via Blackbox)
```promql
# Probe success rate
probe_success

# HTTP response time
probe_duration_seconds

# HTTP status codes
probe_http_status_code

# SSL certificate expiry
probe_ssl_earliest_cert_expiry
```

### 4. Prometheus Internal Metrics
```promql
# Ingestion rate
rate(prometheus_tsdb_head_samples_appended_total[5m])

# Active time series
prometheus_tsdb_head_series

# Storage usage
prometheus_tsdb_head_chunks_created_total
```

## Query Examples

### Performance Monitoring
```promql
# CPU usage percentage
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage percentage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage percentage
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100
```

### Application Monitoring
```promql
# Service availability
avg_over_time(probe_success[5m])

# Response time 95th percentile
histogram_quantile(0.95, rate(probe_duration_seconds_bucket[5m]))

# Error rate
rate(probe_success == 0[5m])
```

### Container Monitoring
```promql
# Container CPU usage
rate(container_cpu_usage_seconds_total[5m]) * 100

# Container memory usage
container_memory_usage_bytes / container_memory_limit_bytes * 100

# Container restart count
increase(container_start_time_seconds[1h])
``` -->

## Storage and Retention

### Time Series Database (TSDB)
- **Storage path**: `/prometheus` (mounted volume)
- **Compression**: Efficient time-series compression
- **Retention**: Default 15 days (configurable)
<!-- - **Block structure**: 2-hour blocks for optimal performance -->


## Network Configuration

- **Port**: 9090 (Web UI and API)
- **Network**: app-net (internal Docker network)
- **Dependencies**: Alloy (for remote write), Blackbox Exporter
- **Web UI**: http://localhost:9090

<!-- 
## API Endpoints

### Query API
- `/api/v1/query` - Instant queries
- `/api/v1/query_range` - Range queries
- `/api/v1/series` - Series metadata
- `/api/v1/labels` - Label names and values

### Management API
- `/api/v1/write` - Remote write endpoint (used by Alloy)
- `/-/reload` - Configuration reload
- `/-/ready` - Readiness check
- `/-/healthy` - Health check

### Web Interface
- `/graph` - Query and graphing interface
- `/targets` - Scrape target status
- `/config` - Current configuration view
- `/rules` - Alerting and recording rules

## Monitoring Capabilities

### Target Health Monitoring
- **Scrape success rate**: Track target availability
- **Scrape duration**: Monitor collection performance
- **Target discovery**: Service discovery status
- **Configuration validation**: Config reload success

### Performance Metrics
- **Ingestion rate**: Samples per second
- **Query performance**: Query execution time
- **Storage usage**: Disk space and growth rate
- **Memory usage**: RAM consumption patterns

## Best Practices

### 1. Metric Design
- **Consistent naming**: Use standard metric naming conventions
- **Appropriate labels**: Use labels for dimensions, not high-cardinality data
- **Metric types**: Choose appropriate types (counter, gauge, histogram, summary)

### 2. Performance Optimization
- **Scrape intervals**: Balance freshness with performance impact
- **Retention policies**: Configure appropriate data retention
- **Query optimization**: Use efficient PromQL queries
- **Resource allocation**: Provide adequate CPU and memory

### 3. Monitoring Strategy
- **SLI/SLO definition**: Define service level indicators and objectives
- **Alert design**: Create meaningful alerts with appropriate thresholds
- **Dashboard organization**: Structure dashboards for different audiences
- **Documentation**: Maintain runbooks for common scenarios

This Prometheus configuration provides comprehensive metrics collection and storage capabilities, serving as the foundation for monitoring and alerting across the entire Docker stack infrastructure. -->
