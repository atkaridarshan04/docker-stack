# Docker Stack

A comprehensive Docker-based application stack featuring a Flask web application with MySQL database, NGINX reverse proxy, and integrated observability tools for monitoring and logging.

## 🏗️ Architecture Overview

![Docker Stack Architecture](assets/architecture/project_arch.png)
*Docker Stack Architecture - Core components and data flow*

This project implements a complete containerized application stack with built-in observability:

- **Application Layer**: Flask web application with MySQL database
- **Reverse Proxy**: NGINX for load balancing and routing
- **Metrics Collection**: Prometheus with Blackbox Exporter for application monitoring
- **Log Aggregation**: Grafana Loki for centralized logging
- **Data Collection**: Grafana Alloy for unified telemetry collection
- **Visualization**: Grafana dashboards for metrics and logs

## 📋 Services

| Service | Port | Description |
|---------|------|-------------|
| **NGINX** | 80 | Reverse proxy and load balancer |
| **Flask App** | 5000 | Python web application |
| **MySQL** | 3306 | Database server |
| **Grafana** | 3000 | Visualization and dashboards |
| **Prometheus** | 9090 | Metrics collection and storage |
| **Loki** | 3100 | Log aggregation system |
| **Alloy** | 12345 | Telemetry data collection agent |
| **Blackbox Exporter** | 9115 | Application health monitoring |

## 🚀 Quick Start

### 1. Clone and Start

```bash
cd docker-stack

# Start all services
./scripts/start.sh
```

### 2. Access Services

- **Application**: http://localhost
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Alloy**: http://localhost:12345


## 🖥️ Service Interfaces

### Flask Application
![Flask Application](assets/flask-app.png)
*Main Flask web application interface*

### Prometheus Monitoring
![Prometheus Targets](assets/prometheus-targets.png)
*Prometheus target monitoring and health status*

### Grafana Alloy
![Alloy Interface](assets/alloy.png)
*Grafana Alloy Components Graph*

![Alloy Graph](assets/alloy-graph.png)
*Alloy data flow and processing graph*

### Blackbox Exporter
![Blackbox Exporter](assets/blackbox-exporter.png)
*Blackbox exporter metrics and probe results*


## 📊 Monitoring Dashboards

The stack includes pre-configured Grafana dashboards for comprehensive observability:

### System Monitoring
- **Node Exporter Dashboard** (ID: 1860) - System metrics and performance
- **Docker Container Dashboard** (ID: 193) - Container resource usage
- **MySQL Dashboard** (ID: 7587) - Database performance metrics
- **Blackbox Exporter Dashboard** (ID: 13639) - Application uptime monitoring

### Dashboard Screenshots

![Grafana Dashboards](assets/grafana/dashboards.png)
*Available Grafana dashboards overview*

![Grafana DataSources](assets/grafana/datasource.png)
*Configured Grafana data sources*

![Node Exporter Dashboard](assets/grafana/dash-node-exporter.png)
*System metrics and performance monitoring*

![Docker Container Dashboard](assets/grafana/dash-docker-monitoring.png)
*Container resource usage and health*

![Blackbox Exporter Dashboard](assets/grafana/dash-blackbox-exporter.png)
*Application uptime and health monitoring*

![Log Analysis](assets/grafana/drilldown-logs.png)
*Centralized log analysis with Loki*

![Metrics Drilldown](assets/grafana/drilldown-metrics.png)
*Detailed metrics analysis and correlation*


## 🔍 Features

### Application Stack
- **Flask Web Application**: Python-based web server with health endpoints
- **MySQL Database**: Persistent data storage with initialization scripts
- **NGINX Reverse Proxy**: Load balancing and request routing
- **Docker Orchestration**: Multi-container deployment with health checks

### Observability
- **Metrics Collection**: Application and system performance monitoring
- **Log Aggregation**: Centralized logging from all services
- **Health Monitoring**: Automated service health checks and alerts
- **Visualization**: Real-time dashboards and analytics

### Domain & SSL Management
- **NGINX Proxy Manager**: Web-based reverse proxy management with SSL automation
- **Let's Encrypt Integration**: Automatic SSL certificate generation and renewal
- **Custom Domain Support**: Easy domain configuration and routing

![NGINX Proxy Manager Interface](./assets/nginx-proxy-manager/app.png)

![Grafana Blackbox Integration](./assets/nginx-proxy-manager/grafana-blackbox.png)
*Grafana dashboard showing Blackbox monitoring through proxy*

For detailed setup and results, see [Domain and SSL Configuration](./nginx-proxy-manager.md).

## Clean Up

```bash
./scripts/stop.sh
```
