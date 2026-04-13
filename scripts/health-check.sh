#!/bin/bash

# ============================================
# PMS Health Check Script
# ============================================

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
TIMEOUT=5
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-}"
EMAIL_TO="${ALERT_EMAIL:-}"

# Exit codes
EXIT_OK=0
EXIT_WARNING=1
EXIT_CRITICAL=2

# Check functions
check_backend() {
    local response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$BACKEND_URL/admin/login/" 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo "✓ Backend is responding (HTTP $response)"
        return $EXIT_OK
    elif [ "$response" = "302" ] || [ "$response" = "301" ]; then
        echo "✓ Backend is responding (HTTP $response - Redirect)"
        return $EXIT_OK
    else
        echo "✗ Backend health check failed (HTTP $response)"
        return $EXIT_CRITICAL
    fi
}

check_database() {
    if docker-compose exec -T db pg_isready -U pms_user &>/dev/null; then
        echo "✓ Database is responding"
        return $EXIT_OK
    else
        echo "✗ Database is not responding"
        return $EXIT_CRITICAL
    fi
}

check_redis() {
    if docker-compose exec -T redis redis-cli ping &>/dev/null; then
        echo "✓ Redis is responding"
        return $EXIT_OK
    else
        echo "✗ Redis is not responding"
        return $EXIT_CRITICAL
    fi
}

check_disk_space() {
    local usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -lt 80 ]; then
        echo "✓ Disk space is OK ($usage% used)"
        return $EXIT_OK
    elif [ "$usage" -lt 90 ]; then
        echo "⚠ Disk space warning ($usage% used)"
        return $EXIT_WARNING
    else
        echo "✗ Disk space critical ($usage% used)"
        return $EXIT_CRITICAL
    fi
}

check_memory() {
    local usage=$(free | awk 'NR==2 {printf "%.0f", $3/$2 * 100}')
    
    if [ "$usage" -lt 80 ]; then
        echo "✓ Memory usage is OK ($usage% used)"
        return $EXIT_OK
    elif [ "$usage" -lt 90 ]; then
        echo "⚠ Memory usage warning ($usage% used)"
        return $EXIT_WARNING
    else
        echo "✗ Memory usage critical ($usage% used)"
        return $EXIT_CRITICAL
    fi
}

send_alert() {
    local message="$1"
    
    # Send to Slack if webhook is configured
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚨 PMS Alert: $message\"}" \
            "$SLACK_WEBHOOK" 2>/dev/null
    fi
    
    # Send email if configured
    if [ -n "$EMAIL_TO" ]; then
        echo "$message" | mail -s "PMS Health Check Alert" "$EMAIL_TO"
    fi
}

# Main health check
main() {
    echo "PMS Health Check - $(date)"
    echo "================================"
    
    local exit_code=$EXIT_OK
    local errors=""
    
    # Run checks
    if ! check_backend; then
        exit_code=$EXIT_CRITICAL
        errors="$errors\n- Backend is down"
    fi
    
    if ! check_database; then
        exit_code=$EXIT_CRITICAL
        errors="$errors\n- Database is down"
    fi
    
    if ! check_redis; then
        exit_code=$EXIT_CRITICAL
        errors="$errors\n- Redis is down"
    fi
    
    local disk_result=$(check_disk_space)
    echo "$disk_result"
    if [ $? -eq $EXIT_CRITICAL ]; then
        exit_code=$EXIT_CRITICAL
        errors="$errors\n- Disk space critical"
    fi
    
    local mem_result=$(check_memory)
    echo "$mem_result"
    if [ $? -eq $EXIT_CRITICAL ]; then
        exit_code=$EXIT_CRITICAL
        errors="$errors\n- Memory usage critical"
    fi
    
    echo "================================"
    
    # Send alerts if needed
    if [ $exit_code -eq $EXIT_CRITICAL ]; then
        echo "❌ Health check FAILED"
        send_alert "Health check failed:$errors"
    elif [ $exit_code -eq $EXIT_WARNING ]; then
        echo "⚠️  Health check WARNING"
    else
        echo "✅ All systems operational"
    fi
    
    exit $exit_code
}

# Run health check
main
