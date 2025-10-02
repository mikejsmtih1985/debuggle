# Getting Started with Debuggle

Welcome to Debuggle! This guide will help you get up and running with our log processing service in just a few minutes.

## 🎯 What is Debuggle?

Debuggle transforms your raw log data into analyzul, structured, and analyzable formats. Whether you're debugging applications, monitoring systems, or analyzing user behavior, Debuggle makes your logs more readable and actionable.

## 🚀 Quick Start

### Step 1: Get Your API Key

1. Sign up at [debuggle.com](https://debuggle.com)
2. Navigate to your dashboard
3. Copy your API key from the "API Keys" section

### Step 2: Make Your First Request

Try this simple example to process a log entry:

```bash
curl -X POST http://localhost:8000/debuggle-log \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "content": "2025-01-01 12:00:00 ERROR: Database connection failed",
    "tier": "core"
  }'
```

**Response:**
```json
{
  "success": true,
  "processed_content": "🔧 [CORE] 2025-01-01 12:00:00 ❌ ERROR: Database connection failed",
  "processing_time": 0.045,
  "tier_used": "core"
}
```

### Step 3: Try the Web Interface

Open your browser to `http://localhost:8000` to use our interactive web interface:

1. Paste your log content into the text area
2. Select your service tier
3. Click "Process Logs"
4. Download or copy the enhanced results

## 🏆 Service Tiers

Choose the tier that best fits your needs:

### 🔧 Core (Free)
- **Daily Limit:** 100 requests
- **Features:** Basic log processing
- **Perfect for:** Personal projects, learning

### ⚡ Pro ($9/month)
- **Daily Limit:** 1,000 requests  
- **Features:** Advanced formatting, custom patterns
- **Perfect for:** Small teams, side projects

### 👥 Team ($29/month)
- **Daily Limit:** 5,000 requests
- **Features:** Team collaboration, shared workspaces
- **Perfect for:** Growing teams, multiple projects

### 🏢 Enterprise ($99/month)
- **Daily Limit:** 25,000 requests
- **Features:** Priority support, custom integrations
- **Perfect for:** Large organizations, mission-critical apps

### 🚀 Scale (Custom)
- **Daily Limit:** 100,000+ requests
- **Features:** Custom solutions, dedicated support
- **Perfect for:** Enterprise scale, high-volume processing

## 📁 Processing Log Files

### Web Upload
1. Visit the web interface at `http://localhost:8000`
2. Click "Choose Files" to select up to 5 log files
3. Select your service tier
4. Click "Process Files"
5. Download the processed results

### API Upload
```bash
curl -X POST http://localhost:8000/upload-file \
  -H "X-API-Key: your-api-key-here" \
  -F "file=@application.log" \
  -F "tier=pro"
```

## 🛠️ Integration Examples

### Python Application
```python
import requests
import logging

class DebuggleHandler(logging.Handler):
    def __init__(self, api_key, tier='core'):
        super().__init__()
        self.api_key = api_key
        self.tier = tier
        self.url = "http://localhost:8000/debuggle-log"
    
    def emit(self, record):
        log_entry = self.format(record)
        try:
            response = requests.post(
                self.url,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.api_key
                },
                json={
                    "content": log_entry,
                    "tier": self.tier
                }
            )
            if response.status_code == 200:
                processed = response.json()["processed_content"]
                print(processed)
        except Exception as e:
            print(f"Failed to process log: {e}")

# Usage
logger = logging.getLogger(__name__)
handler = DebuggleHandler("your-api-key", "pro")
logger.addHandler(handler)
logger.error("Database connection failed")
```

### Node.js Application
```javascript
const axios = require('axios');

class DebuggleLogger {
    constructor(apiKey, tier = 'core') {
        this.apiKey = apiKey;
        this.tier = tier;
        this.url = 'http://localhost:8000/debuggle-log';
    }
    
    async log(content) {
        try {
            const response = await axios.post(this.url, {
                content: content,
                tier: this.tier
            }, {
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': this.apiKey
                }
            });
            
            console.log(response.data.processed_content);
            return response.data;
        } catch (error) {
            console.error('Failed to process log:', error.message);
        }
    }
}

// Usage
const logger = new DebuggleLogger('your-api-key', 'pro');
logger.log('ERROR: Something went wrong');
```

## 🎨 Output Formats

Debuggle enhances your logs with:

- **🎯 Tier indicators** - Visual service tier badges
- **📅 Timestamp formatting** - Consistent, readable timestamps  
- **🎨 Log level styling** - Color-coded error levels
- **📊 Structured data** - JSON parsing and formatting
- **🔍 Pattern recognition** - Automatic detection of common patterns

## 🔧 Configuration

### Environment Variables
Create a `.env` file in your project:

```env
DEBUGGLE_API_KEY=your-api-key-here
DEBUGGLE_TIER=pro
DEBUGGLE_BASE_URL=http://localhost:8000
```

### Configuration File
Create `debuggle.config.json`:

```json
{
  "apiKey": "your-api-key-here",
  "defaultTier": "pro",
  "baseUrl": "http://localhost:8000",
  "timeout": 30,
  "retries": 3
}
```

## 🆘 Troubleshooting

### Common Issues

**Q: Getting "Invalid API Key" error?**
A: Verify your API key is correct and passed in the `X-API-Key` header.

**Q: Rate limit exceeded?**
A: Check your tier limits or upgrade to a higher tier for more requests.

**Q: Large files not processing?**
A: Files must be under 10MB. Split larger files or upgrade to Enterprise tier.

**Q: Slow processing times?**
A: Large files and complex patterns take longer. Consider upgrading tiers for priority processing.

## 📚 Next Steps

- [Explore Advanced Features](./features.md)
- [Understand Service Tiers](./tiers.md)
- [API Reference](../api/README.md)
- [Deployment Guide](../deployment/docker.md)

## 💬 Get Help

- 📖 [Full Documentation](../README.md)
- 🐛 [Report Issues](https://github.com/mikejsmtih1985/debuggle/issues)
- 💬 [Community Discord](https://discord.gg/debuggle)
- 📧 [Support Email](mailto:support@debuggle.com)