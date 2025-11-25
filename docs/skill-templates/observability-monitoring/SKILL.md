---
name: Observability with Prometheus & Grafana
skill_id: observability-monitoring
version: 1.0.0
description: Production-grade observability stack with Prometheus metrics, Grafana dashboards, PromQL query language, alerting rules, and AI-powered anomaly detection for modern cloud-native applications
category: DevOps & Infrastructure
tags:
  - observability
  - monitoring
  - prometheus
  - grafana
  - metrics
  - alerting
  - promql
  - sre
  - cloud-native
  - ai-observability
author: mcp-skillset
license: MIT
created: 2025-11-25
last_updated: 2025-11-25
toolchain:
  - Prometheus 2.45+
  - Grafana 10.0+
  - Alertmanager
  - Node Exporter
  - Blackbox Exporter
frameworks:
  - Prometheus
  - Grafana
  - OpenTelemetry
related_skills:
  - terraform-infrastructure
  - fastapi-web-development
  - postgresql-optimization
  - systematic-debugging
---

# Observability with Prometheus & Grafana

## Overview

Master production observability with Prometheus and Grafana - the industry-standard monitoring stack for cloud-native applications. Learn metrics collection, PromQL query language, dashboard design, alerting, and AI-powered anomaly detection (Grafana AI Observability 2024).

## When to Use This Skill

- Monitoring production applications and infrastructure
- Implementing SLOs (Service Level Objectives) and SLIs
- Creating custom metrics for business KPIs
- Setting up alerting for proactive incident response
- Debugging performance issues with metrics analysis
- Tracking API latency, error rates, and throughput
- Monitoring AI/ML model performance in production

## Core Principles

### 1. The Four Golden Signals (Google SRE)

```yaml
# Always monitor these four metrics for every service:

# 1. Latency - How long requests take
http_request_duration_seconds_bucket{le="0.1", job="api"} 8500
http_request_duration_seconds_bucket{le="0.5", job="api"} 9800
http_request_duration_seconds_sum{job="api"} 2450
http_request_duration_seconds_count{job="api"} 10000

# 2. Traffic - How many requests
http_requests_total{method="GET", status="200"} 50000

# 3. Errors - How many requests fail
http_requests_total{method="POST", status="500"} 150

# 4. Saturation - How "full" is the service
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes < 0.2
```

### 2. Metric Types

```python
from prometheus_client import Counter, Gauge, Histogram, Summary, Info

# Counter - Monotonically increasing (requests, errors)
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
request_count.labels(method='GET', endpoint='/api/users', status='200').inc()

# Gauge - Can go up or down (memory usage, queue size)
active_connections = Gauge(
    'active_database_connections',
    'Number of active database connections'
)
active_connections.set(25)
active_connections.inc()  # Increment
active_connections.dec()  # Decrement

# Histogram - Track distributions (latency, request sizes)
request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]  # Define buckets
)
with request_duration.time():
    process_request()

# Summary - Similar to histogram, calculates quantiles
response_size = Summary(
    'http_response_size_bytes',
    'HTTP response size in bytes'
)
response_size.observe(1024)

# Info - Static metadata
app_info = Info('app_version', 'Application version info')
app_info.info({'version': '1.2.3', 'environment': 'production'})
```

**When to use each type**:
- **Counter**: Total requests, errors, bytes transferred
- **Gauge**: Current memory, active users, queue depth
- **Histogram**: Request latency, response sizes (use for percentiles)
- **Summary**: Similar to histogram, cheaper but less flexible

### 3. PromQL Essentials

```promql
# Basic queries
http_requests_total  # Instant vector (latest value)
http_requests_total[5m]  # Range vector (5 minute window)

# Label matching
http_requests_total{method="GET"}  # Exact match
http_requests_total{method=~"GET|POST"}  # Regex match
http_requests_total{method!="OPTIONS"}  # Not equal

# Aggregation operators
sum(rate(http_requests_total[5m])) by (status)  # Requests per second by status
avg(http_request_duration_seconds) by (endpoint)  # Average latency by endpoint
max(node_memory_MemTotal_bytes) without (instance)  # Max memory across instances

# Rate and increase (for counters)
rate(http_requests_total[5m])  # Per-second rate over 5 minutes
increase(http_requests_total[1h])  # Total increase over 1 hour
irate(http_requests_total[5m])  # Instant rate (sensitive to spikes)

# Histogram quantiles (percentiles)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))  # p95 latency
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))  # p99 latency

# Math and comparisons
(sum(rate(http_requests_total{status=~"5.."}[5m]))
 / sum(rate(http_requests_total[5m]))) * 100  # Error rate percentage

node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes < 0.1  # Memory <10%

# Logical operators
(rate(http_requests_total[5m]) > 100) and (http_request_duration_seconds > 1)
```

### 4. Alerting Rules

```yaml
# /etc/prometheus/alerts.yml
groups:
  - name: api_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          (sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
           / sum(rate(http_requests_total[5m])) by (service)) > 0.05
        for: 5m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "High error rate on {{ $labels.service }}"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"
          runbook: "https://wiki.company.com/runbooks/high-error-rate"

      # High latency (p99)
      - alert: HighLatency
        expr: |
          histogram_quantile(0.99,
            rate(http_request_duration_seconds_bucket[5m])
          ) > 1.0
        for: 10m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "P99 latency above 1s"
          description: "P99 latency is {{ $value }}s on {{ $labels.instance }}"

      # Service down
      - alert: ServiceDown
        expr: up{job="api"} == 0
        for: 1m
        labels:
          severity: critical
          page: true
        annotations:
          summary: "Service {{ $labels.instance }} is down"

      # Database connection exhaustion
      - alert: DatabaseConnectionsHigh
        expr: |
          pg_stat_database_numbackends / pg_settings_max_connections > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connections at {{ $value | humanizePercentage }}"

# Alertmanager configuration (/etc/alertmanager/alertmanager.yml)
route:
  receiver: 'team-backend'
  group_by: ['alertname', 'cluster']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
    - match:
        severity: warning
      receiver: 'slack-warnings'

receivers:
  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: '<PAGERDUTY_KEY>'

  - name: 'slack-warnings'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/XXX'
        channel: '#alerts'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

### 5. Grafana Dashboard Design

```json
{
  "dashboard": {
    "title": "API Performance Dashboard",
    "panels": [
      {
        "title": "Request Rate (RPS)",
        "targets": [{
          "expr": "sum(rate(http_requests_total[5m])) by (service)",
          "legendFormat": "{{ service }}"
        }],
        "type": "graph"
      },
      {
        "title": "Error Rate (%)",
        "targets": [{
          "expr": "(sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m]))) * 100",
          "legendFormat": "Error Rate"
        }],
        "type": "graph",
        "alert": {
          "conditions": [{"evaluator": {"params": [5], "type": "gt"}}],
          "frequency": "60s",
          "message": "Error rate above 5%"
        }
      },
      {
        "title": "Latency Percentiles",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p50"
          },
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p99"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

## Best Practices

### Metric Naming Conventions

```
# Format: <namespace>_<subsystem>_<name>_<unit>

http_requests_total           # Counter: total requests
http_request_duration_seconds # Histogram: request duration
process_cpu_seconds_total     # Counter: CPU time
node_memory_bytes             # Gauge: memory in bytes

# Use base units:
- seconds (not milliseconds)
- bytes (not KB/MB)
- ratio (0.0-1.0, not percentage)
```

### Label Best Practices

```python
# GOOD: Low-cardinality labels
http_requests_total{method="GET", status="200", endpoint="/api/users"}

# BAD: High-cardinality labels (creates too many time series)
http_requests_total{user_id="12345"}  # DON'T: user_id has millions of values!
http_requests_total{ip_address="192.168.1.1"}  # DON'T: IP has too many values

# GOOD: Aggregate high-cardinality data
user_requests_total  # Single metric without user_id label
```

**Rule of thumb**: Total cardinality = product of label values. Keep <10,000 per metric.

### Recording Rules (Pre-compute Expensive Queries)

```yaml
# /etc/prometheus/rules.yml
groups:
  - name: api_performance
    interval: 30s
    rules:
      # Pre-calculate p99 latency (expensive query)
      - record: job:http_request_duration_seconds:p99
        expr: |
          histogram_quantile(0.99,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (job, le)
          )

      # Pre-calculate error rate
      - record: job:http_requests:error_rate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) by (job)
          / sum(rate(http_requests_total[5m])) by (job)

# Use in dashboards/alerts:
# job:http_request_duration_seconds:p99 > 1.0
```

## FastAPI Integration Example

```python
from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
import time

app = FastAPI()

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['method', 'endpoint']
)

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    method = request.method
    endpoint = request.url.path

    ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).inc()

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(
        method=method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()

    REQUEST_DURATION.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)

    ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).dec()

    return response

# Expose metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Prometheus scrapes: GET http://localhost:8000/metrics
```

## Common Anti-Patterns

### ❌ DON'T: Alert on symptoms without context

```yaml
# BAD: Alert fires constantly during deploys
- alert: HighCPU
  expr: node_cpu_seconds_total > 80
  for: 1m  # Too short!

# GOOD: Alert with context and reasonable threshold
- alert: SustainedHighCPU
  expr: |
    (100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)) > 80
  for: 10m  # Grace period
  annotations:
    description: "CPU >80% for 10 minutes on {{ $labels.instance }}"
```

### ❌ DON'T: Create dashboards without purpose

```
# GOOD Dashboard Hierarchy:
1. Executive Dashboard (business metrics, SLOs)
2. Service Dashboard (RED metrics: Rate, Errors, Duration)
3. Resource Dashboard (CPU, memory, disk, network)
4. Debug Dashboard (detailed metrics for troubleshooting)

# BAD: 50 panels on one dashboard with no organization
```

## AI-Powered Observability (2024)

```yaml
# Grafana AI Observability features:

# 1. Anomaly Detection
# Automatically detects unusual patterns in metrics
# (configured in Grafana UI, not code)

# 2. Predictive Alerts
# ML models predict future resource exhaustion
- alert: PredictedDiskFull
  expr: predict_linear(node_filesystem_avail_bytes[1h], 4*3600) < 0
  annotations:
    summary: "Disk will be full in 4 hours"

# 3. Root Cause Analysis
# Grafana Correlate plugin finds related metrics during incidents

# 4. AIOps Recommendations
# Suggests optimal alert thresholds based on historical data
```

## Related Skills

- **terraform-infrastructure**: Provision Prometheus/Grafana with IaC
- **fastapi-web-development**: Add metrics to FastAPI applications
- **postgresql-optimization**: Monitor PostgreSQL with postgres_exporter
- **systematic-debugging**: Use metrics to debug production issues

## Additional Resources

- Prometheus Documentation: https://prometheus.io/docs
- Grafana Documentation: https://grafana.com/docs
- PromQL Tutorial: https://promlabs.com/promql-cheat-sheet
- SRE Book (Google): https://sre.google/sre-book/monitoring-distributed-systems

## Example Questions

- "How do I create a histogram metric for API latency?"
- "Write a PromQL query for p99 latency over 5 minutes"
- "How do I alert when error rate exceeds 5%?"
- "Show me how to integrate Prometheus with FastAPI"
- "What's the difference between rate() and irate()?"
- "How do I create a Grafana dashboard for service health?"
