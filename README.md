# 🐞 Debuggle - Trace Level

**Log beautification and error analysis microservice**

Debuggle Trace Level is the first tier of the Debuggle ecosystem - a powerful microservice that transforms ugly, hard-to-read error logs and stack traces into beautifully formatted, easy-to-understand output with intelligent summaries and categorization.

## ✨ Features

### 🎨 **Log Beautification**
- **Syntax highlighting** with support for Python, JavaScript, Java, C#, C++, Go, and Rust
- **Smart formatting** and cleanup of messy stack traces
- **De-duplication** of repetitive error lines
- **Auto-detection** of programming languages from log content

### 🧠 **Intelligent Analysis**
- **Plain-English summaries** for common error types (IndexError, KeyError, NullPointerException, etc.)
- **Smart tagging** system for error categorization
- **Pattern recognition** for known error types across multiple languages

### 🚀 **Production Ready**
- **FastAPI-powered** REST API with automatic OpenAPI documentation
- **Rate limiting** and input validation for production use
- **Docker containerization** with health checks
- **Comprehensive test suite** with 95%+ coverage
- **Environment-based configuration** management

## 🐜 Service Tiers

- **🐜 Trace Level** (Current) - Log beautification, syntax highlighting, smart summaries
- **🐝 Swarm Level** (Coming Soon) - Log grouping, pattern detection, basic storage
- **🪲 Beetle Level** (Planned) - Persistent storage, dashboard UI, search & filter
- **🕷️ Spider Level** (Planned) - Proactive alerts, integrations, team collaboration  
- **🦋 Butterfly Level** (Planned) - AI insights, SSO, compliance, enterprise features

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional)

### Method 1: Local Development

1. **Clone and install dependencies:**
```bash
git clone <your-repo-url>
cd debuggle
pip install -r requirements.txt
```

2. **Start the development server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Or use the Makefile
make dev
```

3. **Visit the API documentation:**
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Method 2: Docker

1. **Using Docker Compose (Recommended):**
```bash
docker-compose up --build
```

2. **Using Docker directly:**
```bash
docker build -t debuggle-trace:latest .
docker run -p 8000:8000 debuggle-trace:latest
```

## 📡 API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Beautify Log
```bash
curl -X POST "http://localhost:8000/api/v1/beautify" \
  -H "Content-Type: application/json" \
  -d '{
    "log_input": "Traceback (most recent call last):\n  File \"app.py\", line 14, in <module>\n    main()\nIndexError: list index out of range",
    "language": "python",
    "options": {
      "highlight": true,
      "summarize": true,
      "tags": true
    }
  }'
```

**Response:**
```json
{
  "cleaned_log": "...",
  "summary": "Your code tried to access a list element that doesn't exist (IndexError).",
  "tags": ["IndexError", "Python", "Error", "StackTrace"],
  "metadata": {
    "lines": 4,
    "language_detected": "python",
    "processing_time_ms": 27,
    "truncated": false
  }
}
```

### Get Available Tiers
```bash
curl http://localhost:8000/api/v1/tiers
```

## 🔧 Configuration

Copy `.env.example` to `.env` and customize:

```bash
# Application settings
DEBUGGLE_APP_NAME="Debuggle Trace Level"
DEBUGGLE_DEBUG=false

# Processing limits
DEBUGGLE_MAX_LOG_SIZE=50000
DEBUGGLE_MAX_LINES=1000
DEBUGGLE_RATE_LIMIT_PER_MINUTE=100

# Features
DEBUGGLE_ENABLE_SUMMARIZATION=true
DEBUGGLE_ENABLE_LANGUAGE_DETECTION=true
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_api.py -v
```

## 🏗️ Development

```bash
# Install dependencies
make install

# Format code
make format

# Lint code  
make lint

# Start development server
make dev
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Supported Languages
- Python
- JavaScript
- Java
- C#
- C++
- Go
- Rust
- Auto-detection

### Supported Error Types
- **Python:** IndexError, KeyError, AttributeError, ImportError, SyntaxError, TypeError, ValueError, etc.
- **JavaScript:** ReferenceError, TypeError, SyntaxError, RangeError
- **Java:** NullPointerException, ArrayIndexOutOfBoundsException, ClassNotFoundException
- **And many more...**

## 🚢 Deployment

### Docker Production
```bash
# Build and run
make build
make up

# Or deploy to your container platform
docker build -t debuggle-trace:$(git rev-parse --short HEAD) .
```

### Cloud Platforms
Debuggle is designed to work seamlessly with:
- **AWS Lambda** (serverless)
- **Google Cloud Run**  
- **Azure Container Instances**
- **Fly.io**
- **Railway**
- **Heroku**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`make test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Documentation:** http://localhost:8000/docs
- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions

---

**Made with ❤️ by the Debuggle Team**
