# NGINX Reverse Proxy Configuration

## Overview

**NGINX** is a high-performance web server and reverse proxy server. In this setup, NGINX acts as a reverse proxy that sits in front of the Flask application, providing load balancing, SSL termination capabilities, and serving as the main entry point for external traffic.

## Role in Current Setup

NGINX serves as the reverse proxy layer that:
- **Routes traffic** from external clients to the Flask application
- **Load balances** requests across application instances (if scaled)
<!-- - **Handles SSL termination** (when configured with certificates) -->
<!-- - **Provides caching** for static content and API responses -->
- **Adds security headers** and request filtering
- **Serves as health check endpoint** for monitoring

## Configuration Structure

The `default.conf` file contains a simple reverse proxy configuration:

### Server Block Configuration

```nginx
server {
    listen 80;                    # Listen on port 80 (HTTP)
    server_name localhost;        # Accept requests for localhost
    
    location / {
        # Proxy all requests to Flask application
        proxy_pass http://flask-app:5000;
        
        # Preserve original request headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Configuration Details

### 1. Server Listening

```nginx
listen 80;
server_name localhost;
```

**Purpose**:
- **Port 80**: Standard HTTP port for web traffic
- **localhost**: Accepts requests for localhost domain
- **Default server**: Handles all HTTP requests on port 80

**Production Considerations**:
- Add specific domain names instead of localhost
- Configure SSL/TLS on port 443
- Implement HTTP to HTTPS redirects

### 2. Location Block

```nginx
location / {
    proxy_pass http://flask-app:5000;
    # ... headers
}
```

**Functionality**:
- **Root location**: Matches all requests (`/`)
- **Upstream target**: Flask application on port 5000
- **Docker networking**: Uses service name `flask-app`

### 3. Proxy Headers

#### Host Header Preservation
```nginx
proxy_set_header Host $host;
```
**Purpose**: Preserves the original Host header from client request, ensuring the Flask app knows the original domain.

#### Real IP Forwarding
```nginx
proxy_set_header X-Real-IP $remote_addr;
```
**Purpose**: Passes the client's real IP address to the Flask application for logging and security.

#### Forwarded For Chain
```nginx
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```
**Purpose**: Maintains the chain of proxy servers, useful for tracking request path through multiple proxies.

#### Protocol Information
```nginx
proxy_set_header X-Forwarded-Proto $scheme;
```
**Purpose**: Informs the Flask app whether the original request was HTTP or HTTPS.

## Network Architecture

```
Internet → Docker Host:80 → NGINX:80 → Flask App:5000
```

### Traffic Flow
1. **External Request**: Client sends HTTP request to localhost:80
2. **NGINX Reception**: NGINX receives request on port 80
3. **Proxy Decision**: Location block matches request path
4. **Backend Forwarding**: Request proxied to flask-app:5000
5. **Response Return**: Flask response sent back through NGINX to client


## Health Checks

### NGINX Health Check
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost/"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

**Monitoring**:
- **Endpoint**: Tests root path availability
- **Frequency**: Every 10 seconds
- **Failure handling**: 5 retries before marking unhealthy

## Performance Features

### Connection Handling
- **Event-driven**: Efficient handling of concurrent connections
- **Keep-alive**: Maintains persistent connections to backend
- **Connection pooling**: Reuses connections to Flask app

### Caching Capabilities
```nginx
# Example caching configuration (not in current setup)
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    proxy_pass http://flask-app:5000;
}
```

### Load Balancing
```nginx
# Example upstream configuration for multiple Flask instances
upstream flask_backend {
    server flask-app-1:5000;
    server flask-app-2:5000;
    server flask-app-3:5000;
}

server {
    location / {
        proxy_pass http://flask_backend;
    }
}
```
<!-- 
## Security Features

### Basic Security Headers
```nginx
# Example security headers (can be added)
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

### Rate Limiting
```nginx
# Example rate limiting (can be added)
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://flask-app:5000;
}
``` -->

## Monitoring Integration

### Access Logs
- **Default location**: `/var/log/nginx/access.log`
- **Format**: Combined log format with request details
- **Collection**: Picked up by Alloy for centralized logging

### Error Logs
- **Default location**: `/var/log/nginx/error.log`
- **Levels**: Error, warning, notice, info, debug
- **Monitoring**: Integrated with log aggregation system

<!-- ### Metrics Exposure
```nginx
# Example stub_status module (can be enabled)
location /nginx_status {
    stub_status on;
    access_log off;
    allow 127.0.0.1;
    deny all;
}
``` -->

<!-- ## Best Practices

1. **Configuration Management**: Use version control for NGINX configs
2. **Security**: Implement proper security headers and rate limiting
3. **Monitoring**: Enable access and error logging
4. **Performance**: Configure appropriate buffer sizes and timeouts
5. **SSL**: Always use HTTPS in production environments
6. **Backup**: Regular backup of configuration files -->

## Troubleshooting

### Common Issues
1. **502 Bad Gateway**: Flask app not responding or unreachable
2. **Connection refused**: Flask app not started or wrong port
3. **DNS resolution**: Service name not resolving in Docker network

### Debug Commands
```bash
# Check NGINX configuration syntax
docker exec nginx-proxy nginx -t

# Reload configuration without restart
docker exec nginx-proxy nginx -s reload

# View access logs
docker logs nginx-proxy

# Test connectivity to Flask app
docker exec nginx-proxy curl http://flask-app:5000
```

This NGINX configuration provides a solid foundation for reverse proxy functionality, with room for expansion to include SSL, caching, load balancing, and advanced security features as the application grows.
