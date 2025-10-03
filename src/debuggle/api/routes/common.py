"""
🩺 Hospital Common Services - Basic System Routes

This module handles the common, system-wide endpoints that every hospital needs:
- Health checks
- Service information  
- Basic system status

Think of this like the hospital's main reception and information desk:
- /health: "Is the hospital operational?" (system health check)
- /: Welcome page and general information
- /api/v1: API information and capabilities
- /tiers: Service levels and pricing information

🏆 HIGH SCHOOL EXPLANATION:
Like a school's main office that provides basic information:
1. "Is the school open today?" (health check)
2. "What services do you offer?" (capabilities)
3. "What are the different programs available?" (service tiers)
4. General welcome and orientation information

NOTE: This is the modular route structure. The route implementations will be
moved here from main.py during the refactoring process.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse

# Create router for common system routes
router = APIRouter(tags=["system"])


from fastapi import Depends
from fastapi.responses import HTMLResponse, JSONResponse

from ...models import HealthResponse, TiersResponse, TierFeature
from ...config_v2 import settings


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
        version=settings.app_version    # Which version we're running
    )


@router.get("/api/v1/tiers", response_model=TiersResponse)
async def get_tiers(tier_manager=Depends(get_tier_manager)):
    """Get available service tiers and their features."""
    try:
        return await tier_manager.get_available_tiers()
    except Exception as e:
        # Fallback if tier system isn't working
        return TiersResponse(
            current_tier="free",
            available_tiers={
                "free": TierFeature(
                    name="Free Tier",
                    description="Basic error analysis",
                    max_requests_per_hour=100,
                    features=["Basic analysis", "File upload", "Search logs"]
                )
            }
        )