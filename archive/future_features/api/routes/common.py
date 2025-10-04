"""
🏥 Hospital Common Services - System-Wide Routes

This is the common services department of our hospital! Like how a real hospital
has reception, information desk, and general services that serve the entire facility,
this module handles system-wide endpoints that don't belong to any specific department.

Think of this like the hospital's main information desk:
- /health: "Is the hospital operating?" (health check)
- /api/v1: "What services do you offer?" (API information)
- /api/v1/tiers: "What service levels are available?" (pricing tiers)

🏆 HIGH SCHOOL EXPLANATION:
Like the main office at school:
1. Front desk that tells you if the school is open today
2. Information board showing what programs are available
3. Counselor explaining different academic tracks you can choose
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime

from ...models import HealthResponse, TiersResponse, TierFeature
from ...config_v2 import settings

# Create router for this department
router = APIRouter(tags=["common"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Hospital Vital Signs Monitor - "Is Our System Healthy?" 💓🏥
    
    This is like a nurse taking the hospital's vital signs every few minutes.
    Other systems (load balancers, monitoring tools, uptime checkers) can
    call this endpoint to make sure our service is still running properly.
    
    It's the digital equivalent of asking "Are you okay?" and getting back
    "Yes, I'm healthy and ready to help patients!"
    
    Real-world usage:
    - Kubernetes uses this to know if it should restart our service
    - Load balancers use this to know if they should send traffic here
    - Monitoring systems use this to alert if something goes wrong
    - Developers use this to quickly check if the service is up
    
    Simple but CRUCIAL for production systems!
    """
    # Return a simple health status - like a thumbs up from the hospital
    return HealthResponse(
        status="ok",                    # "We're healthy and ready to serve!"
        service=settings.app_name,      # Which service this is (Debuggle Core)
        version=settings.app_version,   # Which version we're running
        response_time=0.001,            # Quick response time
        details={"uptime": "healthy"},  # Additional status details
        metrics={},                     # Performance metrics
        timestamp=datetime.utcnow().timestamp()  # When this check was performed
    )


@router.get("/api/v1/tiers", response_model=TiersResponse)
async def get_tiers():
    """Get available service tiers and their features."""
    # Simple tier information without complex dependencies
    tiers = [
        TierFeature(
            name="Core",
            description="Essential log analysis features",
            included=True
        ),
        TierFeature(
            name="Pro", 
            description="Advanced features with alerting",
            included=False
        ),
        TierFeature(
            name="Team",
            description="Collaboration and dashboard features", 
            included=False
        )
    ]
    
    return TiersResponse(
        current_tier="Core",
        available_tiers={
            "tiers": tiers
        }
    )


@router.get("/api/v1", response_class=JSONResponse)
async def api_info():
    """API Information - What services does this hospital offer?"""
    return {
        "service": "Debuggle API",
        "version": settings.app_version,
        "description": "Intelligent log analysis and error debugging service",
        "endpoints": {
            "health": "/health",
            "analyze": "/api/v1/analyze", 
            "upload": "/api/v1/upload-log",
            "search": "/api/v1/search",
            "tiers": "/api/v1/tiers"
        },
        "documentation": "/docs"
    }


@router.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - serve basic HTML interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debuggle - Intelligent Log Analysis</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            h1 { color: #2c3e50; }
            .feature { margin: 10px 0; padding: 10px; background: #ecf0f1; border-radius: 5px; }
            .api-link { display: inline-block; margin: 10px; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 Debuggle - Intelligent Log Analysis</h1>
            <p>Welcome to Debuggle, your intelligent log analysis and error debugging service!</p>
            
            <h2>🚀 Features</h2>
            <div class="feature">📊 Smart error analysis with context</div>
            <div class="feature">🔍 Advanced log search and filtering</div>
            <div class="feature">📁 File upload support</div>
            <div class="feature">⚡ Real-time monitoring</div>
            
            <h2>📚 API Documentation</h2>
            <a href="/docs" class="api-link">Interactive API Docs</a>
            <a href="/api/v1" class="api-link">API Information</a>
            <a href="/health" class="api-link">Health Check</a>
            
            <h2>🧪 Try Live Error Analysis</h2>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <textarea id="errorInput" placeholder="Paste your error log here..." style="width: 100%; height: 100px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-family: monospace;"></textarea>
                <br><br>
                <button onclick="analyzeError()" style="background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;">🔍 Analyze Error</button>
                <div id="result" style="margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 4px; display: none;">
                    <h4>Analysis Result:</h4>
                    <div id="resultContent"></div>
                </div>
            </div>
            
            <script>
            async function analyzeError() {
                const input = document.getElementById('errorInput').value;
                const resultDiv = document.getElementById('result');
                const contentDiv = document.getElementById('resultContent');
                
                if (!input.trim()) {
                    alert('Please enter an error message to analyze');
                    return;
                }
                
                try {
                    contentDiv.innerHTML = '<div style="color: #007bff;">🔄 Analyzing your error...</div>';
                    resultDiv.style.display = 'block';
                    
                    const response = await fetch('/api/v1/analyze', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            log_input: input,
                            language: 'auto'
                        })
                    });
                    
                    const data = await response.json();
                    
                    contentDiv.innerHTML = `
                        <div style="margin: 10px 0;">
                            <strong>📝 Summary:</strong><br>
                            <div style="background: white; padding: 10px; border-radius: 4px; margin: 5px 0;">${data.summary}</div>
                        </div>
                        <div style="margin: 10px 0;">
                            <strong>🏷️ Tags:</strong><br>
                            <div style="margin: 5px 0;">${data.tags.map(tag => `<span style="background: #007bff; color: white; padding: 3px 8px; border-radius: 12px; margin: 2px; display: inline-block; font-size: 12px;">${tag}</span>`).join('')}</div>
                        </div>
                        <div style="margin: 10px 0;">
                            <strong>🛠️ Processed Log:</strong><br>
                            <pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; white-space: pre-wrap; font-size: 12px;">${data.cleaned_log}</pre>
                        </div>
                    `;
                } catch (error) {
                    contentDiv.innerHTML = `<div style="color: #dc3545;">❌ Error: ${error.message}</div>`;
                }
            }
            </script>
        </div>
    </body>
    </html>
    """