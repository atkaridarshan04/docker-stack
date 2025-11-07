# Blackbox Exporter Configuration

## Overview

**Blackbox Exporter** is a Prometheus exporter that allows probing of endpoints over HTTP, HTTPS, DNS, TCP, and ICMP. It performs "black box" monitoring by testing services from the outside, simulating how users would interact with your applications. This is complementary to "white box" monitoring (internal metrics).

## Role in Current Setup

Blackbox Exporter provides external health monitoring for the Docker stack by:
- **HTTP/HTTPS endpoint monitoring** - Tests web application availability and response times
- **TCP connectivity checks** - Verifies service ports are accessible
- **Service health validation** - Ensures services respond correctly to requests
<!-- - **Network connectivity testing** - ICMP ping tests for basic connectivity
- **Protocol-specific probes** - SSH, gRPC, and other service checks -->

## Configuration Structure

The `blackbox.yml` file defines various probe modules that can be used to test different types of services:

### 1. HTTP Probes

```yaml
# Basic HTTP GET request expecting 2xx status codes
http_2xx:
  prober: http                    # Use HTTP prober
  http:
    preferred_ip_protocol: "ip4"  # Prefer IPv4 over IPv6
```

```yaml
# HTTP POST request probe
http_post_2xx:
  prober: http
  http:
    method: POST                  # Use POST method instead of GET
```

**Use Cases:**
- Web application health checks
- API endpoint availability
- Load balancer health verification
- SSL certificate validation

<!-- ### 2. TCP Connection Probes

```yaml
# Basic TCP connectivity test
tcp_connect:
  prober: tcp                     # Use TCP prober for port connectivity
```

**Use Cases:**
- Database connection testing
- Service port availability
- Network connectivity verification
- Load balancer backend checks

### 3. Secure Email (POP3S) Probe

```yaml
# POP3S email server probe
pop3s_banner:
  prober: tcp
  tcp:
    query_response:
    - expect: "^+OK"              # Expect POP3 greeting message
    tls: true                     # Use TLS encryption
    tls_config:
      insecure_skip_verify: false # Verify SSL certificates
```

**Use Cases:**
- Email server availability
- SSL/TLS certificate validation
- Mail service health monitoring

### 4. gRPC Service Probes

```yaml
# Secure gRPC service probe
grpc:
  prober: grpc
  grpc:
    tls: true                     # Use TLS encryption
    preferred_ip_protocol: "ip4"  # Prefer IPv4

# Plain gRPC service probe (no TLS)
grpc_plain:
  prober: grpc
  grpc:
    tls: false                    # No encryption
    service: "service1"           # Specific service to probe
```

**Use Cases:**
- Microservice health checks
- gRPC API availability
- Service mesh monitoring

### 5. SSH Service Probes

```yaml
# Basic SSH banner check
ssh_banner:
  prober: tcp
  tcp:
    query_response:
    - expect: "^SSH-2.0-"         # Expect SSH protocol banner
    - send: "SSH-2.0-blackbox-ssh-check"  # Send identification string
```

```yaml
# Advanced SSH probe with version extraction
ssh_banner_extract:
  prober: tcp
  timeout: 5s                     # 5-second timeout
  tcp:
    query_response:
    - expect: "^SSH-2.0-([^ -]+)(?: (.*))?$"  # Regex to capture version info
      labels:
      - name: ssh_version         # Extract SSH version
        value: "${1}"
      - name: ssh_comments        # Extract additional comments
        value: "${2}"
```

**Use Cases:**
- SSH server availability
- Version information collection
- Security compliance monitoring
- Remote access verification

### 6. IRC Service Probe

```yaml
# IRC server connectivity and authentication
irc_banner:
  prober: tcp
  tcp:
    query_response:
    - send: "NICK prober"         # Set nickname
    - send: "USER prober prober prober :prober"  # User registration
    - expect: "PING :([^ ]+)"     # Wait for server ping
      send: "PONG ${1}"           # Respond to ping
    - expect: "^:[^ ]+ 001"       # Wait for welcome message
```

**Use Cases:**
- Chat server monitoring
- IRC network health checks
- Real-time communication service testing

### 7. ICMP (Ping) Probes

```yaml
# Basic ICMP ping
icmp:
  prober: icmp                    # Use ICMP prober

# ICMP with custom TTL
icmp_ttl5:
  prober: icmp
  timeout: 5s                     # 5-second timeout
  icmp:
    ttl: 5                        # Set Time To Live to 5 hops
```

**Use Cases:**
- Network connectivity testing
- Latency measurement
- Network path analysis
- Basic reachability checks -->

## Integration with Prometheus

Blackbox Exporter is typically configured in Prometheus to probe specific targets:

```yaml
# Example Prometheus job configuration
- job_name: 'blackbox-http'
  metrics_path: /probe
  params:
    module: [http_2xx]            # Use http_2xx module
  static_configs:
    - targets:
      - http://flask-app:5000     # Target to probe
      - http://nginx              # Another target
  relabel_configs:
    - source_labels: [__address__]
      target_label: __param_target
    - source_labels: [__param_target]
      target_label: instance
    - target_label: __address__
      replacement: blackbox-exporter:9115  # Blackbox exporter address
```

## Metrics Generated

Blackbox Exporter generates several key metrics:

### Probe Success Metrics
- `probe_success` - Whether the probe succeeded (1) or failed (0)
- `probe_duration_seconds` - Time taken to complete the probe

### HTTP-Specific Metrics
- `probe_http_status_code` - HTTP response status code
- `probe_http_content_length` - Response content length
- `probe_http_ssl` - Whether SSL was used
- `probe_http_redirects` - Number of redirects followed

### TCP-Specific Metrics
- `probe_tcp_connect_time_seconds` - Time to establish TCP connection

### SSL/TLS Metrics
- `probe_ssl_earliest_cert_expiry` - Earliest SSL certificate expiry time
- `probe_ssl_last_chain_expiry_timestamp_seconds` - Certificate chain expiry