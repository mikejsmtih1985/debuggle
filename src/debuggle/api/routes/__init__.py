"""🏥 HOSPITAL DEPARTMENTS - Specialized Medical Services! 🏥

This is where all our medical departments are organized, each with
its own specialty and expertise. Instead of having one giant room
where all doctors try to handle every type of case, we have
specialized departments for focused, expert care.

🏥 MEDICAL DEPARTMENTS:
- analysis.py: 🔬 Analysis Lab - Error diagnosis specialists
- upload.py: 📁 File Processing Dept - Document handling experts
- dashboard.py: 📊 Analytics Center - Data visualization specialists
- realtime.py: 📡 Communications Hub - Live monitoring experts
- alerts.py: 🚨 Emergency Response - Critical alert specialists
- ingestion.py: 🏭 Processing Plant - Batch operation experts
- health.py: 💓 Vital Signs Monitor - System health experts
- info.py: ℹ️ Information Desk - General information services

Each department has its own trained specialists who know exactly
how to handle their specific type of cases!
"""

from fastapi import FastAPI
import logging

# Set up logging for our department coordination system
logger = logging.getLogger(__name__)

def register_all_routes(app: FastAPI):
    """
    🏥 CONNECT ALL MEDICAL DEPARTMENTS! 🏥
    
    This function connects all our specialized medical departments
    to the main hospital building, ensuring patients can access
    every service we offer through a unified system.
    """
    
    logger.info("🏥 Connecting all medical departments to main hospital...")
    
    # For Phase 1, we'll add basic endpoints to get started
    add_basic_endpoints(app)
    
    logger.info("✅ Basic hospital services connected and operational!")


def add_basic_endpoints(app: FastAPI):
    """
    🏥 ADD BASIC HOSPITAL SERVICES - Essential Endpoints! 🏥
    
    This adds the most basic services that our hospital needs to
    function, serving as a foundation while we build out the
    specialized departments.
    """
    from fastapi.responses import JSONResponse, HTMLResponse
    import os
    import time
    from ...config_v2 import settings
    
    @app.get("/", response_class=HTMLResponse)
    async def hospital_main_entrance():
        """🏥 Main Hospital Entrance - Welcome patients!"""
        try:
            with open("assets/static/index.html", "r") as f:
                return HTMLResponse(content=f.read())
        except FileNotFoundError:
            return HTMLResponse(content="""
            <html>
                <head><title>Debuggle Digital Hospital</title></head>
                <body>
                    <h1>🏥 Welcome to Debuggle Digital Hospital!</h1>
                    <p>Your error analysis specialists are ready to help.</p>
                    <p><a href="/docs">📖 View our service directory</a></p>
                </body>
            </html>
            """)
    
    @app.get("/api/v1", response_class=JSONResponse)
    async def hospital_information_desk():
        """ℹ️ Hospital Information Desk - Service directory"""
        return {
            "hospital": settings.app_name,
            "version": settings.app_version,
            "status": "operational",
            "services": {
                "emergency": "/docs",
                "analysis_lab": "/api/v1/analyze",
                "file_processing": "/api/v1/upload-log",
                "vital_signs": "/health",
                "communications": "/ws/errors"
            },
            "welcome_message": "🏥 Welcome to Debuggle Digital Hospital - Professional Error Analysis Services",
            "timestamp": time.time()
        }
    
    @app.get("/health", response_class=JSONResponse)
    async def hospital_vital_signs():
        """💓 Hospital Vital Signs - System health check"""
        return {
            "status": "healthy",
            "hospital": settings.app_name,
            "version": settings.app_version,
            "timestamp": time.time(),
            "departments": {
                "analysis_lab": "operational",
                "file_processing": "operational", 
                "communications": "operational",
                "information_desk": "operational"
            }
        }

    logger.info("✅ Basic hospital services added and operational")


# Export our department coordination system
__all__ = ["register_all_routes", "add_basic_endpoints"]
