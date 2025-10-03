"""
🏥 HOSPITAL CONSTRUCTION MANAGER - FastAPI App Factory! 🏥

This file is like the master architect and construction foreman who builds
our entire digital hospital from the ground up. Instead of having everything
mixed together in one giant file, this creates a clean, organized facility
where each department knows its role.

🏗️ CONSTRUCTION PROCESS:
1. Design the hospital blueprint (FastAPI app configuration)
2. Install the foundation systems (middleware, CORS, rate limiting)
3. Wire up the infrastructure (dependency injection, monitoring)
4. Build each department (register API routes)
5. Set up patient amenities (static files, documentation)
6. Open the doors for business (return completed app)

This replaces the old main.py approach where everything was mixed together.
Now we have a professional construction process that builds hospitals
(FastAPI apps) to order!

🏆 HIGH SCHOOL EXPLANATION:
Think of this like a master contractor who builds custom hospitals:
- They follow a detailed blueprint (this function)
- They coordinate all the specialists (other modules)
- They ensure everything is connected properly (dependencies)
- They do quality control testing (error handling)
- They hand over a complete, working facility (FastAPI app)

This is what makes Debuggle better than ChatGPT - we have a complete,
integrated system with proper architecture instead of just a chat interface!
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import logging

# Import our hospital construction materials and specialists
from .config_v2 import settings
from .realtime import connection_manager, error_monitor
from .self_monitor import setup_self_monitoring

# Set up logging for our construction process
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """
    🏗️ BUILD A COMPLETE DIGITAL HOSPITAL! 🏗️
    
    This function constructs a fully-equipped digital hospital (FastAPI app)
    with all departments, systems, and services properly organized and
    connected. Like hiring a master architect to build a world-class
    medical facility!
    
    🏥 WHAT GETS BUILT:
    - 🏢 Main hospital building (FastAPI app)
    - 🚪 Reception and security (middleware, CORS, rate limiting)  
    - 🏥 All medical departments (API routes organized by specialty)
    - 🔧 Support systems (monitoring, dependency injection)
    - 📚 Patient information center (documentation, static files)
    - 📡 Communication systems (WebSocket, real-time monitoring)
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like those amazing "hospital construction" TV shows where
    they show how a modern medical facility gets built from the ground up:
    - First they pour the foundation (basic FastAPI app)
    - Then they install all the infrastructure (middleware, security)
    - Then they build each department (routes for different services)
    - Finally they add all the finishing touches (static files, docs)
    
    When it's done, you have a complete, professional facility ready
    to serve patients (handle API requests) efficiently!
    
    Returns:
        FastAPI: A complete, fully-equipped digital hospital ready to serve patients!
    """
    
    logger.info("🏗️ Starting digital hospital construction...")
    
    # Step 1: Design the hospital blueprint (FastAPI app configuration)
    logger.info("📐 Designing hospital blueprint...")
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version, 
        description="🐞 Debuggle Core - Professional log analysis and error diagnosis microservice",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    logger.info(f"✅ Hospital blueprint designed: {settings.app_name} v{settings.app_version}")
    
    # Step 2: Install foundation systems (middleware, security, monitoring)
    logger.info("🔧 Installing hospital infrastructure...")
    setup_middleware(app)
    logger.info("✅ Security and traffic control systems installed")
    
    # Step 3: Set up hospital supply chain (dependency injection)
    logger.info("📦 Setting up hospital supply chain...")
    setup_dependencies(app)
    logger.info("✅ Medical equipment and supply chain ready")
    
    # Step 4: Build all medical departments (register API routes)
    logger.info("🏥 Building medical departments...")
    register_all_routes(app)
    logger.info("✅ All medical departments operational")
    
    # Step 5: Install patient amenities (static files)
    logger.info("📚 Setting up patient information center...")
    setup_static_files(app)
    logger.info("✅ Patient information and UI systems ready")
    
    # Step 6: Activate monitoring systems
    logger.info("📡 Activating hospital monitoring systems...")
    try:
        setup_self_monitoring(app, connection_manager)
        logger.info("✅ Real-time monitoring systems active")
    except Exception as e:
        logger.warning(f"⚠️ Monitoring system setup failed: {e} - continuing without self-monitoring")
    
    # Step 7: Initialize cloud features (if available)
    logger.info("☁️ Checking for cloud integration...")
    setup_cloud_features(app)
    
    logger.info("🎉 Digital hospital construction complete! Ready to serve patients.")
    logger.info(f"🌐 Hospital accessible at: http://localhost:8000")
    logger.info(f"📖 Documentation available at: http://localhost:8000/docs")
    
    return app


def setup_middleware(app: FastAPI):
    """
    🚪 HOSPITAL SECURITY & TRAFFIC CONTROL - Middleware Setup! 🚪
    
    This sets up all the security systems and traffic control measures
    for our digital hospital, like having security guards, traffic directors,
    and emergency protocols in place.
    
    🏆 HIGH SCHOOL EXPLANATION:
    Think of this like setting up all the security and traffic systems
    for a busy hospital:
    - Security guards check everyone who enters (CORS middleware)
    - Traffic directors prevent overcrowding (rate limiting)
    - Emergency protocols handle unexpected problems (error handling)
    - International patient services (CORS for cross-origin requests)
    """
    from .api.middleware import setup_all_middleware
    setup_all_middleware(app)


def setup_dependencies(app: FastAPI):
    """
    📦 HOSPITAL SUPPLY CHAIN - Dependency Injection Setup! 📦
    
    This sets up our hospital's supply chain and equipment inventory
    management system, ensuring that every department has access to
    the medical equipment and supplies it needs.
    
    🏆 HIGH SCHOOL EXPLANATION:  
    This is like setting up the supply chain management for a hospital:
    - Medical equipment gets delivered where needed (dependency injection)
    - Inventory management ensures nothing runs out (singleton patterns)
    - Quality control ensures all equipment works properly (validation)
    """
    from .dependencies import setup_all_dependencies
    setup_all_dependencies(app)


def register_all_routes(app: FastAPI):
    """
    🏥 MEDICAL DEPARTMENTS SETUP - Route Registration! 🏥
    
    This builds and connects all our medical departments to the main
    hospital building, ensuring patients can find the right specialist
    for their specific needs.
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like connecting all the different medical departments to
    the main hospital reception:
    - Cardiology department (analysis routes)
    - Radiology department (upload routes)  
    - Emergency department (alert routes)
    - Laboratory (dashboard routes)
    Each department has its own entrance but they're all part of one hospital!
    """
    from .api.routes import register_all_routes as register_routes
    register_routes(app)


def setup_static_files(app: FastAPI):
    """
    📚 PATIENT INFORMATION CENTER - Static File Setup! 📚
    
    This sets up the hospital's information center where patients can
    access brochures, forms, and educational materials (HTML, CSS, JS files).
    Like having a well-organized information desk with all the resources
    patients need.
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like setting up the information desk and waiting room in a hospital:
    - Brochures and educational materials (HTML files)
    - Forms patients might need (CSS styling)
    - Interactive kiosks (JavaScript functionality)
    Everything patients need while they wait or learn about services!
    """
    static_dir = "assets/static"
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        logger.info(f"✅ Patient information center ready at: {static_dir}")
    else:
        logger.warning(f"⚠️ Information center directory not found: {static_dir}")


def setup_cloud_features(app: FastAPI):
    """
    ☁️ SATELLITE CLINICS - Cloud Integration Setup! ☁️
    
    This sets up our satellite clinic network (cloud features) that extends
    our main hospital's capabilities. These are optional but provide additional
    services when available.
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like setting up satellite clinics that work with the main hospital:
    - Remote consultations (cloud sharing)
    - Specialist referrals (cloud deployment)
    - Medical record sharing between facilities (cloud storage)
    If the satellite clinics aren't available, the main hospital still works perfectly!
    """
    try:
        from .cloud import setup_cloud_routes
        
        # Detect current tier (free by default, can be upgraded)
        current_tier = os.getenv("DEBUGGLE_TIER", "free")
        cloud_enabled = os.getenv("DEBUGGLE_CLOUD_ENABLED", "true").lower() == "true"
        
        if cloud_enabled:
            # Add cloud endpoints to existing app (completely additive!)
            setup_cloud_routes(app, tier=current_tier)
            logger.info(f"☁️ Satellite clinic network enabled for {current_tier} tier")
        else:
            logger.info("🏠 Running in local-only mode (satellite clinics disabled)")
            
    except ImportError:
        logger.info("🏠 Satellite clinics not available - running in local-only mode")
    except Exception as e:
        logger.warning(f"⚠️ Satellite clinic setup failed: {e} - continuing with local-only mode")


# For backward compatibility during transition period
# This allows existing code to still import 'app' directly if needed
_app_instance = None

def get_app() -> FastAPI:
    """Get a singleton app instance for backward compatibility."""
    global _app_instance
    if _app_instance is None:
        _app_instance = create_app()
    return _app_instance

# Create the app instance for immediate use (backward compatibility)
app = get_app()