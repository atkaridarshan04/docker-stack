# Grafana Loki Configuration

## Overview

**Grafana Loki** is a horizontally scalable, highly available, multi-tenant log aggregation system inspired by Prometheus. Unlike other logging systems, Loki is designed to be cost-effective and easy to operate by not indexing the contents of logs, but rather a set of labels for each log stream.

## Role in Current Setup

Loki serves as the centralized log aggregation system that:
- **Collects logs** from all Docker containers via Alloy
- **Stores log data** efficiently with minimal indexing
- **Provides log querying** through LogQL (Loki Query Language)
- **Integrates with Grafana** for log visualization and correlation
- **Enables log-based alerting** and monitoring

## Configuration Structure

The `loki.yml` file configures Loki for single-node deployment with filesystem storage:

### 1. Authentication and Security

```yaml
auth_enabled: false  # Disable multi-tenancy for single-node setup
```

**Purpose**: Simplifies deployment for development/testing environments. In production, enable authentication for security.

### 2. Server Configuration

```yaml
server:
  http_listen_port: 3100  # HTTP API port for log ingestion and queries
```

**Endpoints**:
- `/loki/api/v1/push` - Log ingestion endpoint (used by Alloy)
- `/loki/api/v1/query` - Log query endpoint (used by Grafana)
- `/loki/api/v1/query_range` - Time range queries
- `/ready` - Health check endpoint

### 3. Common Configuration

```yaml
common:
  instance_addr: 127.0.0.1     # Instance address for clustering
  path_prefix: /loki           # Base path for all Loki data
  storage:
    filesystem:
      chunks_directory: /loki/chunks  # Log chunk storage location
      rules_directory: /loki/rules    # Alerting rules storage
  replication_factor: 1        # Single replica (no clustering)
  ring:
    kvstore:
      store: inmemory         # In-memory key-value store for single node
```

**Storage Details**:
- **Chunks**: Compressed log data stored in filesystem
- **Rules**: Alert and recording rule definitions
- **Single Node**: No replication for simplified deployment

### 4. Query Performance

```yaml
query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true          # Enable query result caching
        max_size_mb: 100      # Cache size limit (100MB)
```

**Benefits**:
- **Faster queries**: Cached results for repeated queries
- **Reduced load**: Less processing for common queries
- **Memory efficient**: Limited cache size prevents memory exhaustion

### 5. Schema Configuration

```yaml
schema_config:
  configs:
    - from: 2020-10-24        # Schema start date
      store: tsdb             # Time Series Database for index
      object_store: filesystem # Filesystem for chunk storage
      schema: v13             # Schema version
      index:
        prefix: index_        # Index file prefix
        period: 24h          # Index rotation period
```

**Schema Details**:
- **TSDB**: Efficient time-series index storage
- **v13 Schema**: Latest schema version with performance improvements
- **24h Period**: Daily index rotation for manageable file sizes

### 6. Limits and Performance

```yaml
limits_config:
  metric_aggregation_enabled: true  # Enable metric extraction from logs
```

**Features**:
- **Log-derived metrics**: Extract metrics from log patterns
- **Rate limiting**: Prevent resource exhaustion
- **Retention policies**: Automatic log cleanup

### 7. Pattern Recognition

```yaml
pattern_ingester:
  enabled: true                    # Enable log pattern detection
  metric_aggregation:
    loki_address: localhost:3100   # Loki instance for metric storage
```

**Capabilities**:
- **Pattern detection**: Automatically identify log patterns
- **Metric generation**: Create metrics from detected patterns
- **Anomaly detection**: Identify unusual log patterns

### 8. Alerting Integration

```yaml
ruler:
  alertmanager_url: http://localhost:9093  # Alertmanager endpoint
```

**Purpose**: Integration with Prometheus Alertmanager for log-based alerts (optional in current setup).

## Data Flow

### Log Ingestion Pipeline
```
Docker Containers → Alloy → Loki → Grafana
                     ↓
                System Logs
```

1. **Collection**: Alloy collects logs from containers and system
2. **Processing**: Alloy adds labels and formats log entries
3. **Ingestion**: Logs sent to Loki via HTTP API
4. **Storage**: Loki stores logs with minimal indexing
5. **Querying**: Grafana queries logs for visualization
<!-- 
### Log Structure

Loki organizes logs using **labels** instead of full-text indexing:

```
{service_name="flask-app", level="error"} 2024-01-01T10:00:00Z Error message here
{service_name="nginx", level="info"} 2024-01-01T10:00:01Z Access log entry
{job="mysql", level="warn"} 2024-01-01T10:00:02Z Slow query warning
```

## LogQL Query Language

### Basic Queries

```logql
# All logs from flask-app service
{service_name="flask-app"}

# Error logs from any service
{level="error"}

# Logs containing "database" in the message
{service_name="flask-app"} |= "database"

# Rate of error logs per minute
rate({level="error"}[1m])
```

### Advanced Queries

```logql
# Top 10 error messages
topk(10, count by (msg) ({level="error"} | json | line_format "{{.msg}}"))

# HTTP 5xx error rate
rate({service_name="nginx"} | json | status >= 500 [5m])

# MySQL slow queries
{job="mysql"} |= "slow query" | logfmt | duration > 1s
``` -->

## Volume Mounts

```yaml
volumes:
  - data_loki:/loki:rw  # Persistent storage for logs and indices
```

## Network Configuration

- **Port**: 3100 (HTTP API)
- **Network**: app-net (internal Docker network)
- **Dependencies**: None (independent service)
- **API Access**: http://loki:3100
<!-- 
## Performance Characteristics

### Storage Efficiency
- **Label-based indexing**: Only indexes labels, not log content
- **Compression**: Efficient log compression reduces storage needs
- **Chunk-based storage**: Optimized for time-series log data

### Query Performance
- **Stream-based**: Queries operate on log streams
- **Parallel processing**: Concurrent query execution
- **Caching**: Result caching for repeated queries

### Scalability
- **Horizontal scaling**: Can be deployed in clustered mode
- **Storage backends**: Supports object storage (S3, GCS, etc.)
- **Multi-tenancy**: Supports multiple isolated tenants -->

## Monitoring and Observability

### Key Metrics
- `loki_ingester_streams` - Number of active log streams
- `loki_ingester_chunks_created_total` - Chunk creation rate
- `loki_request_duration_seconds` - Query performance
- `loki_distributor_bytes_received_total` - Ingestion rate

### Health Checks
- `/ready` - Service readiness
- `/metrics` - Prometheus metrics
- `/config` - Current configuration

<!-- 
## Integration Points

### With Alloy
- **Push API**: Receives logs via `/loki/api/v1/push`
- **Label processing**: Accepts structured labels from Alloy
- **Batch ingestion**: Handles batched log entries efficiently

### With Grafana
- **Data source**: Configured as Loki data source
- **LogQL support**: Full query language integration
- **Log correlation**: Links logs with metrics for troubleshooting

### With Prometheus
- **Metric extraction**: Generates metrics from log patterns
- **Alert integration**: Log-based alerting rules
- **Label consistency**: Shared label conventions -->

<!-- ## Best Practices

1. **Label Design**: Use consistent, low-cardinality labels
2. **Log Formatting**: Structure logs with consistent formats
3. **Retention**: Configure appropriate retention policies
4. **Monitoring**: Monitor Loki's own metrics and performance
5. **Backup**: Regular backup of critical log data
 -->
