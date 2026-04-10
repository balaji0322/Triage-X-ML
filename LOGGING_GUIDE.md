# 📝 Triage-X - Logging Guide

## Overview

Triage-X uses **Loguru** for structured, colorful, and production-ready logging. The logging system automatically adapts based on the environment.

---

## 🎯 Features

- **Environment-aware**: Automatically switches between development, production, and testing modes
- **Colored output**: Easy-to-read console logs in development
- **File rotation**: Automatic log file management in production
- **Multiple log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Thread-safe**: Safe for concurrent requests
- **Compression**: Automatic log compression to save disk space
- **Retention policies**: Automatic cleanup of old logs

---

## 🔧 Configuration

### Environment Variable

Set the `ENVIRONMENT` variable to control logging behavior:

```bash
# Development (default)
export ENVIRONMENT=development

# Production
export ENVIRONMENT=production

# Testing
export ENVIRONMENT=testing
```

### Development Mode (Default)

**Features**:
- Colorful console output
- DEBUG level and above
- Detailed format with file/function/line info
- No file output

**Log Format**:
```
2024-04-10 13:45:12.769 | INFO     | app.main:predict:45 | ✅ Inference: predicted Urgent (code 1) with confidence 0.9234
```

**Usage**:
```bash
cd backend
uvicorn app.main:app --reload
```

### Production Mode

**Features**:
- File output with rotation
- INFO level and above
- Separate error log file
- Plain text format (no colors)
- Automatic compression
- 30-day retention for main logs
- 90-day retention for error logs

**Log Files**:
- `logs/triage.log` - Main log (INFO+)
- `logs/triage_errors.log` - Error log (ERROR+)

**Log Format**:
```
2024-04-10 13:45:12.769 | INFO     | app.main:predict:45 | ✅ Inference: predicted Urgent (code 1) with confidence 0.9234
```

**Usage**:
```bash
cd backend
export ENVIRONMENT=production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Testing Mode

**Features**:
- Minimal console output
- WARNING level and above
- Simple format

**Usage**:
```bash
export ENVIRONMENT=testing
pytest
```

---

## 📊 Log Levels

### DEBUG
Detailed diagnostic information for troubleshooting.

**Examples**:
```python
log.debug("📥 Received prediction request")
log.debug(f"Patient data: age={age}, HR={hr}, O2={o2}")
log.debug("🔍 SHAP explanation requested")
```

### INFO
General informational messages about system operation.

**Examples**:
```python
log.info("🚀 TRIAGE‑X service ready")
log.info(f"✅ Inference: predicted {severity} with confidence {conf:.4f}")
log.info(f"✅ SHAP explanation generated for {severity} prediction")
```

### WARNING
Indicates potential issues that don't prevent operation.

**Examples**:
```python
log.warning("⚠️ Model confidence below threshold")
log.warning(f"⚠️ Unknown environment '{env}', using default logging")
```

### ERROR
Error events that might still allow the application to continue.

**Examples**:
```python
log.error(f"❌ Invalid payload: {exc}")
log.error(f"❌ Prediction failed: {e}")
log.error("❌ SHAP not installed")
```

### CRITICAL
Very severe error events that might cause the application to abort.

**Examples**:
```python
log.critical("❌ Failed to load model artifacts")
log.critical("❌ Database connection lost")
```

---

## 📝 Log Messages

### Startup/Shutdown

```
2024-04-10 13:45:10.123 | INFO | 🚀 TRIAGE‑X service starting...
2024-04-10 13:45:10.456 | INFO | ✅ Model artifacts loaded successfully
2024-04-10 13:45:10.789 | INFO | 🚀 TRIAGE‑X service ready
2024-04-10 14:30:00.000 | INFO | 🛑 TRIAGE‑X service shutting down
```

### Predictions

```
2024-04-10 13:45:12.123 | DEBUG | 📥 Received prediction request
2024-04-10 13:45:12.456 | DEBUG | Patient data: age=68, HR=110, O2=88
2024-04-10 13:45:12.789 | INFO  | ✅ Inference: predicted Urgent (code 1) with confidence 0.9234
```

### Feature Importance

```
2024-04-10 13:46:00.123 | DEBUG | 📊 Feature importance requested
2024-04-10 13:46:00.456 | INFO  | ✅ Returned 17 feature importance scores
```

### SHAP Explanations

```
2024-04-10 13:47:00.123 | DEBUG | 🔍 SHAP explanation requested
2024-04-10 13:47:00.456 | DEBUG | Computing SHAP values for Urgent prediction
2024-04-10 13:47:01.789 | INFO  | ✅ SHAP explanation generated for Urgent prediction (17 features)
```

### Errors

```
2024-04-10 13:48:00.123 | ERROR | ❌ Invalid payload: missing required field 'age'
2024-04-10 13:48:30.456 | ERROR | ❌ Prediction failed: model not loaded
2024-04-10 13:49:00.789 | ERROR | ❌ SHAP not installed
```

### Health Checks

```
2024-04-10 13:50:00.123 | DEBUG | 🏓 Ping received
```

---

## 🔍 Viewing Logs

### Development (Console)

Logs appear directly in the terminal where uvicorn is running:

```bash
cd backend
uvicorn app.main:app --reload
```

### Production (Files)

**View live logs**:
```bash
# Main log
tail -f logs/triage.log

# Error log
tail -f logs/triage_errors.log

# Last 100 lines
tail -n 100 logs/triage.log
```

**Search logs**:
```bash
# Find all predictions
grep "Inference" logs/triage.log

# Find errors
grep "ERROR" logs/triage.log

# Find specific severity
grep "Urgent" logs/triage.log

# Count predictions by severity
grep "Inference" logs/triage.log | grep -o "predicted [A-Za-z]*" | sort | uniq -c
```

**Analyze logs**:
```bash
# Count log levels
awk '{print $4}' logs/triage.log | sort | uniq -c

# Average confidence scores
grep "confidence" logs/triage.log | grep -o "confidence [0-9.]*" | awk '{sum+=$2; count++} END {print sum/count}'

# Predictions per hour
grep "Inference" logs/triage.log | awk '{print $2}' | cut -d: -f1 | sort | uniq -c
```

---

## 🗂️ Log Rotation

### Automatic Rotation

**Main log** (`logs/triage.log`):
- Rotates when file reaches **10 MB**
- Keeps logs for **30 days**
- Compresses old logs to `.zip`

**Error log** (`logs/triage_errors.log`):
- Rotates when file reaches **5 MB**
- Keeps logs for **90 days**
- Compresses old logs to `.zip`

### Manual Rotation

```bash
# Archive current logs
mv logs/triage.log logs/triage_$(date +%Y%m%d).log
mv logs/triage_errors.log logs/triage_errors_$(date +%Y%m%d).log

# Restart service to create new log files
```

---

## 🐳 Docker Logging

### View Docker Container Logs

```bash
# View logs
docker logs triage-backend

# Follow logs
docker logs -f triage-backend

# Last 100 lines
docker logs --tail 100 triage-backend

# With timestamps
docker logs -t triage-backend
```

### Docker Compose Logs

```bash
# All services
docker-compose logs

# Follow all services
docker-compose logs -f

# Specific service
docker-compose logs backend

# Last 50 lines
docker-compose logs --tail 50 backend
```

### Persist Logs from Docker

Add volume mount in `docker-compose.yml`:

```yaml
services:
  backend:
    volumes:
      - ./logs:/app/logs
    environment:
      - ENVIRONMENT=production
```

---

## 📈 Monitoring & Alerting

### Log Aggregation Tools

**Recommended tools for production**:

1. **ELK Stack** (Elasticsearch, Logstash, Kibana)
   - Full-text search
   - Real-time dashboards
   - Alerting

2. **Grafana Loki**
   - Lightweight
   - Integrates with Grafana
   - Cost-effective

3. **Datadog**
   - Cloud-based
   - APM integration
   - Easy setup

4. **CloudWatch** (AWS)
   - Native AWS integration
   - Automatic log collection
   - Alarms

### Custom Alerts

**Example: Alert on errors**

```bash
#!/bin/bash
# alert_on_errors.sh

ERROR_COUNT=$(grep -c "ERROR" logs/triage.log)

if [ $ERROR_COUNT -gt 10 ]; then
    echo "⚠️ High error count: $ERROR_COUNT errors detected"
    # Send email, Slack notification, etc.
fi
```

**Run as cron job**:
```bash
# Check every 5 minutes
*/5 * * * * /path/to/alert_on_errors.sh
```

---

## 🧪 Testing Logs

### Capture Logs in Tests

```python
# test_logging.py
from loguru import logger as log
import pytest

def test_prediction_logging(caplog):
    """Test that predictions are logged correctly."""
    with caplog.at_level("INFO"):
        # Make prediction
        response = client.post("/predict", json=patient_data)
        
        # Check logs
        assert "Inference: predicted" in caplog.text
        assert "confidence" in caplog.text
```

---

## 🔒 Security Considerations

### Don't Log Sensitive Data

**❌ Bad**:
```python
log.info(f"Patient SSN: {ssn}, Name: {name}")
```

**✅ Good**:
```python
log.info(f"Patient ID: {patient_id}, Age: {age}")
```

### Sanitize Logs

```python
def sanitize_patient_data(data):
    """Remove PII from patient data for logging."""
    safe_data = {
        "age": data.get("age"),
        "heart_rate": data.get("heart_rate"),
        "oxygen_saturation": data.get("oxygen_saturation"),
        # Don't log: name, SSN, address, etc.
    }
    return safe_data

log.debug(f"Patient data: {sanitize_patient_data(patient_data)}")
```

---

## 📊 Log Analysis Examples

### Count Predictions by Severity

```bash
grep "Inference" logs/triage.log | \
  grep -o "predicted [A-Za-z]*" | \
  sort | uniq -c | sort -rn
```

**Output**:
```
  450 predicted Minor
  320 predicted Moderate
  180 predicted Urgent
   50 predicted Immediate
```

### Average Confidence by Severity

```bash
# Extract severity and confidence
grep "Inference" logs/triage.log | \
  awk '{
    for(i=1;i<=NF;i++) {
      if($i=="predicted") severity=$(i+1);
      if($i=="confidence") conf=$(i+1);
    }
    sum[severity]+=conf;
    count[severity]++;
  }
  END {
    for(s in sum) printf "%s: %.4f\n", s, sum[s]/count[s]
  }'
```

### Error Rate

```bash
TOTAL=$(wc -l < logs/triage.log)
ERRORS=$(grep -c "ERROR" logs/triage.log)
ERROR_RATE=$(echo "scale=4; $ERRORS / $TOTAL * 100" | bc)
echo "Error rate: $ERROR_RATE%"
```

---

## 🛠️ Customization

### Add Custom Log Sink

Edit `backend/app/logger.py`:

```python
# Add Slack notifications for errors
import requests

def slack_sink(message):
    """Send ERROR logs to Slack."""
    if "ERROR" in message:
        requests.post(
            "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
            json={"text": message}
        )

log.add(slack_sink, level="ERROR")
```

### Add JSON Logging

```python
# JSON format for log aggregation tools
log.add(
    "logs/triage.json",
    format="{time} {level} {message}",
    serialize=True,  # JSON format
    level="INFO"
)
```

### Add Request ID Tracking

```python
# middleware.py
import uuid
from contextvars import ContextVar

request_id_var = ContextVar("request_id", default=None)

@app.middleware("http")
async def add_request_id(request, call_next):
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    
    log.info(f"[{request_id}] {request.method} {request.url.path}")
    response = await call_next(request)
    
    return response
```

---

## 📚 Resources

- **Loguru Documentation**: https://loguru.readthedocs.io/
- **FastAPI Logging**: https://fastapi.tiangolo.com/tutorial/logging/
- **Python Logging Best Practices**: https://docs.python.org/3/howto/logging.html

---

## ✅ Quick Reference

### Change Log Level

```bash
# Development (DEBUG)
export ENVIRONMENT=development

# Production (INFO)
export ENVIRONMENT=production

# Testing (WARNING)
export ENVIRONMENT=testing
```

### View Logs

```bash
# Console (development)
uvicorn app.main:app --reload

# Files (production)
tail -f logs/triage.log
tail -f logs/triage_errors.log
```

### Search Logs

```bash
# Find predictions
grep "Inference" logs/triage.log

# Find errors
grep "ERROR" logs/triage.log

# Count by severity
grep "predicted" logs/triage.log | cut -d' ' -f10 | sort | uniq -c
```

---

**Last Updated**: April 10, 2026
**Version**: 1.0.0
**Status**: ✅ PRODUCTION READY
