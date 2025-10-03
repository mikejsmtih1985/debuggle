"""
🚪 HOSPITAL SECURITY & TRAFFIC CONTROL - Middleware Systems! 🚪

This file is like the security department and traffic control center
of our digital hospital. It handles all the behind-the-scenes work
that keeps patients safe and ensures smooth traffic flow throughout
the facility.

🛡️ SECURITY SYSTEMS:
- CORS (Cross-Origin Resource Sharing) - like international patient services
- Rate limiting - like preventing overcrowding in waiting rooms
- Error handling - like having emergency protocols for unexpected situations
- Request logging - like having security cameras and visitor logs

🏥 TRAFFIC CONTROL:
- Request routing - like having clear directional signs
- Load management - like managing patient flow during busy times
- Queue management - like having organized waiting systems
- Priority handling - like fast-tracking emergency cases

🏆 HIGH SCHOOL EXPLANATION:
Think of this like all the invisible systems that make a hospital run smoothly:
- Security guards checking IDs (CORS)
- Traffic directors preventing bottlenecks (rate limiting)
- Emergency response teams (error handlers)
- Information systems tracking everything (logging)

You don't see these systems as a patient, but they're essential for
keeping everything safe and running efficiently!
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import time
from typing import Dict, Any

from ..config_v2 import settings

# Set up logging for our security and traffic systems
logger = logging.getLogger(__name__)

# Initialize our traffic control system (rate limiter)
limiter = Limiter(key_func=get_remote_address)

def setup_all_middleware(app: FastAPI):
    """
    🏗️ INSTALL ALL HOSPITAL SECURITY & TRAFFIC SYSTEMS! 🏗️
    
    This function installs all the middleware systems that keep our
    digital hospital safe and running efficiently. Like having a
    professional security company install all the necessary systems
    for a modern medical facility.
    
    🛡️ SECURITY INSTALLATIONS:
    - International patient services (CORS)
    - Traffic flow management (rate limiting)
    - Emergency response protocols (error handling)
    - Visitor tracking systems (request logging)
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like having a security company come in and install:
    - Access control systems (who can enter from where)
    - Traffic management (prevent overcrowding)
    - Emergency protocols (what to do when things go wrong)
    - Monitoring systems (keep track of what's happening)
    """
    
    logger.info("🛡️ Installing hospital security systems...")
    
    # Install traffic control system (rate limiting)
    setup_rate_limiting(app)
    
    # Install international patient services (CORS)
    setup_cors_middleware(app)
    
    # Install emergency response protocols (error handling)
    setup_error_handling(app)
    
    # Install visitor tracking system (request logging)
    setup_request_logging(app)
    
    logger.info("✅ All security and traffic control systems installed!")


def setup_rate_limiting(app: FastAPI):
    """
    🚦 TRAFFIC FLOW MANAGEMENT - Rate Limiting Setup! 🚦
    
    This prevents any single visitor from overwhelming our hospital
    by making too many requests too quickly. Like having traffic
    directors who ensure smooth flow and prevent bottlenecks.
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like having rules at a popular restaurant:
    - "No more than 10 orders per minute per customer"
    - "If you order too fast, please wait a moment"
    - "This keeps the kitchen from getting overwhelmed"
    - "Everyone gets better service when traffic flows smoothly"
    """
    logger.info("🚦 Installing traffic control systems...")
    
    # Attach the rate limiter to our app
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    logger.info("✅ Traffic control systems active")


def setup_cors_middleware(app: FastAPI):
    """
    🌍 INTERNATIONAL PATIENT SERVICES - CORS Setup! 🌍
    
    CORS (Cross-Origin Resource Sharing) allows our hospital to serve
    patients coming from different websites and applications. Like
    having international patient services that can handle visitors
    from anywhere in the world.
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like having a hospital that accepts patients from anywhere:
    - Patients from other cities (different domains)
    - International patients (cross-origin requests)
    - Emergency transfers from other hospitals (different websites)
    - Medical tourists (mobile apps, different origins)
    
    Without this, browsers would block requests from other websites
    for security reasons, like a hospital only accepting local patients.
    """
    logger.info("🌍 Setting up international patient services...")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],          # Accept patients from anywhere
        allow_credentials=True,       # Allow patient ID cards and credentials
        allow_methods=["*"],          # Allow all types of requests (GET, POST, etc.)
        allow_headers=["*"],          # Allow all types of request headers
    )
    
    logger.info("✅ International patient services ready")


def setup_error_handling(app: FastAPI):
    """
    🚨 EMERGENCY RESPONSE PROTOCOLS - Error Handling Setup! 🚨
    
    This sets up our emergency response system that handles unexpected
    problems gracefully. Like having trained emergency response teams
    who know exactly what to do when something goes wrong.
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like having emergency protocols at a hospital:
    - Medical emergencies (unexpected server errors)
    - Equipment failures (dependency problems)
    - Communication breakdowns (network issues)
    - Patient information privacy (security errors)
    
    Instead of the whole hospital shutting down, the emergency team
    handles the problem and keeps everything else running smoothly.
    """
    logger.info("🚨 Installing emergency response protocols...")
    
    @app.exception_handler(Exception)
    async def general_emergency_handler(request: Request, exc: Exception):
        """
        🚨 GENERAL EMERGENCY RESPONSE PROTOCOL! 🚨
        
        This is like the master emergency protocol that kicks in when
        ANYTHING unexpected happens in our hospital. Instead of letting
        the whole system crash, we handle the emergency professionally
        and keep serving other patients.
        
        🏆 HIGH SCHOOL EXPLANATION:
        This is like having a "Code Blue" system in a hospital:
        - Something unexpected happens anywhere in the building
        - The emergency team responds immediately
        - They handle the situation professionally
        - Other patients continue receiving care
        - Detailed incident report gets filed
        - System learns from what happened
        """
        
        # Log the emergency for our medical records
        logger.error(f"🚨 Emergency response activated: {type(exc).__name__}: {exc}")
        logger.error(f"📍 Location: {request.method} {request.url}")
        
        # Determine appropriate emergency response level
        if isinstance(exc, HTTPException):
            # This is a controlled medical procedure (expected HTTP error)
            # Like a planned surgery - we know how to handle this
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "status": "controlled_procedure",
                    "message": exc.detail,
                    "type": "http_exception",
                    "timestamp": time.time()
                }
            )
        else:
            # This is an unexpected emergency (server error)
            # Like a medical emergency - handle it but don't panic
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "emergency_handled",
                    "message": "An unexpected situation occurred. Our emergency team is handling it.",
                    "type": "server_emergency",
                    "timestamp": time.time(),
                    # Show technical details only in debug mode (like showing X-rays only to doctors)
                    "details": str(exc) if settings.debug else "Internal server emergency - please contact support",
                    "error_id": f"{type(exc).__name__}_{int(time.time())}"
                }
            )
    
    @app.exception_handler(RateLimitExceeded)
    async def traffic_control_handler(request: Request, exc: RateLimitExceeded):
        """
        🚦 TRAFFIC CONTROL RESPONSE - Rate Limit Handler! 🚦
        
        This handles situations where someone is making requests too quickly,
        like a traffic director who politely asks people to slow down
        when there's congestion.
        """
        logger.warning(f"🚦 Traffic control activated: {request.client.host} exceeded rate limit")
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "status": "traffic_control",
                "message": "Please slow down! You're making requests too quickly.",
                "type": "rate_limit_exceeded", 
                "retry_after": "Please wait a moment before trying again",
                "timestamp": time.time()
            }
        )
    
    logger.info("✅ Emergency response protocols active")


def setup_request_logging(app: FastAPI):
    """
    📋 VISITOR TRACKING SYSTEM - Request Logging Setup! 📋
    
    This sets up our visitor tracking system that keeps records of
    who visits our hospital and what services they use. Like having
    a visitor log at the front desk.
    
    🏆 HIGH SCHOOL EXPLANATION:
    This is like having a visitor check-in system at a hospital:
    - Who visited (IP address)
    - When they came (timestamp)
    - What department they visited (endpoint)
    - How long their visit took (response time)
    - Whether everything went smoothly (status code)
    
    This helps us improve our services and handle any issues that arise.
    """
    logger.info("📋 Installing visitor tracking system...")
    
    @app.middleware("http")
    async def visitor_tracking_middleware(request: Request, call_next):
        """
        📋 VISITOR CHECK-IN SYSTEM! 📋
        
        This is like the automatic check-in system at a modern hospital
        that tracks visitors and their experience to help improve services.
        """
        
        # Record visitor arrival
        start_time = time.time()
        visitor_ip = request.client.host if request.client else "unknown"
        
        logger.info(f"👋 Visitor arrived: {visitor_ip} → {request.method} {request.url.path}")
        
        # Process the visitor's request
        response = await call_next(request)
        
        # Record visitor departure and experience
        end_time = time.time()
        visit_duration = end_time - start_time
        
        logger.info(
            f"👋 Visitor departed: {visitor_ip} → "
            f"Status: {response.status_code} | "
            f"Duration: {visit_duration:.3f}s"
        )
        
        # Add visitor tracking header to response
        response.headers["X-Visit-Duration"] = f"{visit_duration:.3f}s"
        response.headers["X-Hospital-Status"] = "operational"
        
        return response
    
    logger.info("✅ Visitor tracking system active")


# Export the limiter so routes can use it for specific endpoint limits
__all__ = ["setup_all_middleware", "limiter"]