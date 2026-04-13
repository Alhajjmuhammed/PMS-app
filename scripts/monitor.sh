#!/bin/bash

# ============================================
# PMS Monitoring Script
# Collects metrics and sends to monitoring service
# ============================================

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
METRICS_FILE="/var/log/pms/metrics.log"

# Timestamp
TIMESTAMP=$(date +%s)

# Collect metrics
collect_metrics() {
    local metrics=""
    
    # System metrics
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    local mem_usage=$(free | awk 'NR==2{printf "%.2f", $3*100/$2 }')
    local disk_usage=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')
    
    # Container metrics (if using Docker)
    if command -v docker &> /dev/null; then
        local backend_cpu=$(docker stats --no-stream --format "{{.CPUPerc}}" pms_backend 2>/dev/null | sed 's/%//')
        local backend_mem=$(docker stats --no-stream --format "{{.MemPerc}}" pms_backend 2>/dev/null | sed 's/%//')
        local db_cpu=$(docker stats --no-stream --format "{{.CPUPerc}}" pms_postgres 2>/dev/null | sed 's/%//')
        local db_mem=$(docker stats --no-stream --format "{{.MemPerc}}" pms_postgres 2>/dev/null | sed 's/%//')
    fi
    
    # Application metrics (response time)
    local response_time=$(curl -o /dev/null -s -w '%{time_total}\n' "$BACKEND_URL/admin/login/" 2>/dev/null)
    
    # Build metrics JSON
    metrics=$(cat <<EOF
{
    "timestamp": $TIMESTAMP,
    "system": {
        "cpu_usage": $cpu_usage,
        "memory_usage": $mem_usage,
        "disk_usage": $disk_usage
    },
    "containers": {
        "backend_cpu": ${backend_cpu:-0},
        "backend_memory": ${backend_mem:-0},
        "db_cpu": ${db_cpu:-0},
        "db_memory": ${db_mem:-0}
    },
    "application": {
        "response_time": $response_time
    }
}
EOF
)
    
    echo "$metrics"
}

# Log metrics
log_metrics() {
    local metrics="$1"
    echo "$metrics" >> "$METRICS_FILE"
    
    # Keep only last 7 days of logs
    find "$(dirname "$METRICS_FILE")" -name "metrics.log" -mtime +7 -delete
}

# Send to monitoring service (optional)
send_to_monitoring() {
    local metrics="$1"
    
    # Example: Send to custom monitoring endpoint
    if [ -n "$MONITORING_URL" ]; then
        curl -X POST -H "Content-Type: application/json" \
            -d "$metrics" \
            "$MONITORING_URL" 2>/dev/null
    fi
    
    # Example: Send to Prometheus Pushgateway
    if [ -n "$PUSHGATEWAY_URL" ]; then
        echo "$metrics" | curl --data-binary @- "$PUSHGATEWAY_URL/metrics/job/pms" 2>/dev/null
    fi
}

# Main
main() {
    local metrics=$(collect_metrics)
    log_metrics "$metrics"
    send_to_monitoring "$metrics"
    
    # Print to stdout for debugging
    echo "$metrics"
}

main
