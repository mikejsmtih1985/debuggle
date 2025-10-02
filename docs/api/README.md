# API Reference

The Debuggle API provides powerful log processing capabilities with professional service tiers.

## 🚀 Base URL

```
https://api.debuggle.com/v1
```

For local development:
```
http://localhost:8000
```

## 🔐 Authentication

All API requests require authentication using an API key passed in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key-here" \
     https://api.debuggle.com/v1/health
```

## 📊 Service Tiers

| Tier | Icon | Daily Limit | Features |
|------|------|-------------|----------|
| Core | 🔧 | 100 requests | Basic log processing |
| Pro | ⚡ | 1,000 requests | Advanced formatting |
| Team | 👥 | 5,000 requests | Team collaboration |
| Enterprise | 🏢 | 25,000 requests | Priority support |
| Scale | 🚀 | 100,000 requests | Custom solutions |

## 🔗 Endpoints

### Health Check
Check API status and connectivity.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00Z",
  "service": "Debuggle Core"
}
```

### Process Logs
Transform and enhance log data.

```http
POST /debuggle-log
```

**Headers:**
- `Content-Type: application/json`
- `X-API-Key: {your-api-key}`

**Request Body:**
```json
{
  "content": "2025-01-01 12:00:00 ERROR: Database connection failed",
  "tier": "core",
  "format": "enhanced"
}
```

**Response:**
```json
{
  "success": true,
  "processed_content": "🔧 [CORE] 2025-01-01 12:00:00 ❌ ERROR: Database connection failed",
  "processing_time": 0.045,
  "tier_used": "core",
  "requests_remaining": 99
}
```

### File Upload
Process log files directly.

```http
POST /upload-file
```

**Headers:**
- `Content-Type: multipart/form-data`
- `X-API-Key: {your-api-key}`

**Form Data:**
- `file`: Log file (max 10MB)
- `tier`: Service tier (optional, defaults to "core")

**Response:**
```json
{
  "success": true,
  "filename": "application.log",
  "lines_processed": 1247,
  "download_url": "/download/processed_application_log_123456.txt",
  "processing_time": 2.34
}
```

## ⚠️ Error Responses

### Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded",
  "tier": "core",
  "limit": 100,
  "reset_time": "2025-01-02T00:00:00Z"
}
```

### Invalid API Key
```json
{
  "error": "Invalid or missing API key",
  "code": "AUTH_REQUIRED"
}
```

### Invalid Tier
```json
{
  "error": "Invalid tier specified",
  "available_tiers": ["core", "pro", "team", "enterprise", "scale"]
}
```

## 📝 Code Examples

### Python
```python
import requests
import json

url = "https://api.debuggle.com/v1/debuggle-log"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "your-api-key-here"
}
data = {
    "content": "ERROR: Something went wrong",
    "tier": "pro",
    "format": "enhanced"
}

response = requests.post(url, headers=headers, json=data)
result = response.json()
print(result["processed_content"])
```

### JavaScript
```javascript
const response = await fetch('https://api.debuggle.com/v1/debuggle-log', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-api-key-here'
  },
  body: JSON.stringify({
    content: 'ERROR: Something went wrong',
    tier: 'pro',
    format: 'enhanced'
  })
});

const result = await response.json();
console.log(result.processed_content);
```

### cURL
```bash
curl -X POST https://api.debuggle.com/v1/debuggle-log \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "content": "ERROR: Something went wrong",
    "tier": "pro",
    "format": "enhanced"
  }'
```

## 🔄 Rate Limiting

Rate limits are applied per API key and tier:

- **Headers returned with each response:**
  - `X-RateLimit-Limit`: Your tier's daily limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: When limits reset (UTC timestamp)

- **Best Practices:**
  - Check remaining requests before making calls
  - Implement exponential backoff for rate limit errors
  - Consider upgrading tiers for higher limits

## 🎯 Next Steps

- [Getting Started Guide](../user-guide/getting-started.md)
- [Service Tier Details](../user-guide/tiers.md)
- [Troubleshooting](../user-guide/troubleshooting.md)