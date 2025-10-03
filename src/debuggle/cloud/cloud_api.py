"""
🌐 CLOUD API ENDPOINTS - The Reception Desk for Cloud Debuggle! 🏢☁️

Think of this like the front desk of a hotel that also has online booking:
- REGULAR HOTEL DESK = Your existing local Debuggle API (always works)
- ONLINE BOOKING SYSTEM = These new cloud endpoints (for sharing & remote access)

🏗️ HIGH SCHOOL EXPLANATION:
Imagine your school has a main office AND an online portal:
- Main office (existing API) = handles everything locally, always available
- Online portal (cloud API) = lets you share assignments, access from home

These new endpoints EXTEND your existing Debuggle without changing anything!
You can still use Debuggle exactly like before, but now you ALSO have cloud features.

🎯 WHAT THESE ENDPOINTS DO:
- /api/v1/cloud/upload = Upload error to cloud storage (like uploading to Google Drive)
- /api/v1/cloud/search = Search your cloud-stored errors (like searching your Drive files)
- /api/v1/cloud/share/{id} = Get shareable link (like creating a Google Drive share link)
- /api/v1/cloud/stats = See your cloud usage (like checking Drive storage used)

🔒 SAFETY FEATURES:
- All endpoints are additive - nothing changes about existing functionality
- Rate limiting prevents abuse of free tier
- 24-hour auto-expiration protects privacy
- Graceful fallback if cloud is unavailable

This is like adding Wi-Fi to a building that already has ethernet - both work!
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import our cloud storage manager
from .cloud_storage import CloudStorageManager, CloudLogEntry, CloudStorageStats

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses (like forms with validation)

class CloudUploadRequest(BaseModel):
    """
    📝 Request format for uploading logs to cloud.
    
    Like a form you fill out when uploading a file to Google Drive:
    - What's the file content?
    - What should we call it?
    - What category does it belong to?
    """
    content: str = Field(..., description="The error log content to upload")
    title: str = Field("", description="Human-readable title (auto-generated if empty)")
    tags: List[str] = Field(default=[], description="Tags for categorization")
    language: str = Field("unknown", description="Programming language detected")
    severity: str = Field("info", description="Error severity level")

class CloudUploadResponse(BaseModel):
    """
    ✅ Response after successfully uploading to cloud.
    
    Like the confirmation you get after uploading a file:
    - Here's your file ID
    - Here's the shareable link
    - Here's when it expires
    """
    success: bool
    log_id: str
    share_url: str
    expires_at: datetime
    message: str
    upgrade_hint: Optional[str] = None  # Conversion hook for Pro tier

class CloudSearchRequest(BaseModel):
    """📋 Request format for searching cloud logs."""
    query: str = Field(..., description="Search query")
    limit: int = Field(20, description="Maximum results to return")
    tags: List[str] = Field(default=[], description="Filter by tags")

class CloudSearchResponse(BaseModel):
    """🔍 Response with search results from cloud."""
    success: bool
    results: List[Dict[str, Any]]  # CloudLogEntry converted to dict
    total_found: int
    search_time_ms: float
    upgrade_hint: Optional[str] = None

class CloudStatsResponse(BaseModel):
    """📊 Response with cloud storage statistics."""
    success: bool
    stats: Dict[str, Any]  # CloudStorageStats converted to dict
    upgrade_hints: List[str] = Field(default=[])

class CloudShareResponse(BaseModel):
    """🔗 Response when accessing a shared cloud log."""
    success: bool
    log_entry: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None  # Full Debuggle analysis
    error_message: Optional[str] = None
    viral_cta: Optional[str] = None  # Call-to-action for viral growth

def setup_cloud_routes(app, processor=None, tier: str = "free"):
    """
    🛠️ Set up cloud API routes on the existing FastAPI app.
    
    HIGH SCHOOL ANALOGY:
    This is like adding new rooms to your school building:
    - The existing classrooms (local API) keep working exactly the same
    - New rooms (cloud API) provide additional functionality
    - Students can use either or both, depending on what they need
    
    This function ADDS routes to your existing FastAPI app without changing anything!
    
    Args:
        app: Your existing FastAPI application
        processor: Your existing LogProcessor (for analyzing shared logs)
        tier: Default tier for cloud features ("free", "pro", "enterprise")
    """
    
    # Initialize cloud storage manager
    cloud_manager = CloudStorageManager(tier=tier)
    
    @app.post("/api/v1/cloud/upload", response_model=CloudUploadResponse)
    async def upload_log_to_cloud(
        request: CloudUploadRequest
    ):
        """
        ⬆️ Upload an error log to cloud storage for sharing.
        
        HIGH SCHOOL EXPLANATION:
        This is like uploading your homework to Google Drive so you can:
        1. Access it from any computer
        2. Share it with your study group
        3. Get help from classmates who can see the same file
        
        Your local Debuggle still works exactly the same - this just ADDS
        the ability to put logs in the cloud when you want to share them!
        
        Example usage:
        ```
        curl -X POST "http://localhost:8000/api/v1/cloud/upload" \\
             -H "Content-Type: application/json" \\
             -d '{
               "content": "IndexError: list index out of range\\nline 42 in main.py",
               "title": "IndexError in user signup",
               "tags": ["python", "critical", "signup"],
               "language": "python",
               "severity": "error"
             }'
        ```
        """
        try:
            # Upload to cloud storage
            cloud_entry = await cloud_manager.upload_log(
                content=request.content,
                title=request.title,
                tags=request.tags,
                language=request.language,
                severity=request.severity
            )
            
            if cloud_entry:
                # Generate upgrade hint for freemium conversion
                upgrade_hint = None
                if tier == "free":
                    upgrade_hint = "💰 Pro users get 90-day retention vs 24-hour free. Upgrade at debuggle.dev/pro"
                
                return CloudUploadResponse(
                    success=True,
                    log_id=cloud_entry.log_id,
                    share_url=cloud_entry.share_url,
                    expires_at=cloud_entry.expires_at,
                    message="✅ Log uploaded to cloud successfully!",
                    upgrade_hint=upgrade_hint
                )
            else:
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to upload log to cloud storage"
                )
                
        except Exception as e:
            logger.error(f"Cloud upload error: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"Upload failed: {str(e)}"
            )
    
    @app.post("/api/v1/cloud/search", response_model=CloudSearchResponse)
    async def search_cloud_logs(
        request: CloudSearchRequest
    ):
        """
        🔍 Search through your cloud-stored error logs.
        
        HIGH SCHOOL EXPLANATION:
        This is like using the search feature in Google Drive to find specific files:
        - Type what you're looking for ("IndexError", "database", etc.)
        - Get back a list of matching error logs you've uploaded
        - Click on any result to see the full analysis
        
        This searches ONLY your cloud-uploaded logs, not your local ones.
        Your local search (existing functionality) continues to work separately!
        
        Example usage:
        ```
        curl -X POST "http://localhost:8000/api/v1/cloud/search" \\
             -H "Content-Type: application/json" \\
             -d '{
               "query": "IndexError",
               "limit": 10,
               "tags": ["python", "critical"]
             }'
        ```
        """
        try:
            start_time = datetime.now()
            
            # Search cloud storage
            results = await cloud_manager.search_logs(
                query=request.query,
                limit=request.limit,
                tags=request.tags if request.tags else None
            )
            
            search_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Convert results to dictionaries for JSON response
            result_dicts = [
                {
                    "log_id": result.log_id,
                    "title": result.title,
                    "content": result.content[:200] + "..." if len(result.content) > 200 else result.content,
                    "share_url": result.share_url,
                    "uploaded_at": result.uploaded_at.isoformat(),
                    "expires_at": result.expires_at.isoformat(),
                    "tags": result.tags,
                    "language": result.language,
                    "severity": result.severity
                }
                for result in results
            ]
            
            # Generate upgrade hint
            upgrade_hint = None
            if tier == "free" and len(results) > 0:
                upgrade_hint = "🧠 Pro users get AI-powered search suggestions and advanced filtering!"
            
            return CloudSearchResponse(
                success=True,
                results=result_dicts,
                total_found=len(results),
                search_time_ms=search_time,
                upgrade_hint=upgrade_hint
            )
            
        except Exception as e:
            logger.error(f"Cloud search error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Search failed: {str(e)}"
            )
    
    @app.get("/api/v1/cloud/share/{log_id}", response_model=CloudShareResponse)
    async def get_shared_log(log_id: str):
        """
        🔗 Get a shared error log and its analysis (public endpoint).
        
        HIGH SCHOOL EXPLANATION:
        This is like clicking on a Google Drive share link that someone sent you:
        1. Someone uploads an error to Debuggle Cloud
        2. They share the link with you (like "debuggle.cloud/share/abc123")
        3. You click the link and see the error AND Debuggle's analysis
        4. You can help debug without needing their computer or login
        
        This endpoint is PUBLIC - anyone with the link can see the error analysis.
        Perfect for getting help from teammates, Stack Overflow, etc!
        
        Example usage:
        ```
        curl "http://localhost:8000/api/v1/cloud/share/abc123def456"
        ```
        """
        try:
            # Get log from cloud storage
            cloud_entry = await cloud_manager.get_log(log_id)
            
            if not cloud_entry:
                raise HTTPException(
                    status_code=404,
                    detail="Shared log not found or expired"
                )
            
            # Analyze the log using existing processor (if available)
            analysis = None
            if processor:
                try:
                    # Use existing LogProcessor to analyze the shared log
                    analysis_result = await processor.analyze_log(cloud_entry.content)
                    analysis = {
                        "summary": analysis_result.get("summary", ""),
                        "suggestions": analysis_result.get("suggestions", []),
                        "severity": analysis_result.get("severity", "info"),
                        "language": analysis_result.get("language", "unknown")
                    }
                except Exception as e:
                    logger.warning(f"Analysis failed for shared log: {e}")
            
            # Convert cloud entry to dict
            log_dict = {
                "log_id": cloud_entry.log_id,
                "title": cloud_entry.title,
                "content": cloud_entry.content,
                "uploaded_at": cloud_entry.uploaded_at.isoformat(),
                "expires_at": cloud_entry.expires_at.isoformat(),
                "tags": cloud_entry.tags,
                "language": cloud_entry.language,
                "severity": cloud_entry.severity
            }
            
            # Generate viral call-to-action
            viral_cta = "🚀 Try Debuggle for your own errors: debuggle.dev/download"
            
            return CloudShareResponse(
                success=True,
                log_entry=log_dict,
                analysis=analysis,
                viral_cta=viral_cta
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting shared log {log_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve shared log: {str(e)}"
            )
    
    @app.get("/api/v1/cloud/stats", response_model=CloudStatsResponse)
    async def get_cloud_stats():
        """
        📊 Get your cloud storage usage statistics.
        
        HIGH SCHOOL EXPLANATION:
        This is like checking your Google Drive storage usage:
        - How many files you've uploaded
        - How much space you're using
        - Which files are expiring soon
        - How many people have viewed your shared links
        
        Helps you understand your usage and decide if you need to upgrade!
        
        Example usage:
        ```
        curl "http://localhost:8000/api/v1/cloud/stats"
        ```
        """
        try:
            stats = await cloud_manager.get_stats()
            
            stats_dict = {
                "total_logs": stats.total_logs,
                "total_size_mb": stats.total_size_mb,
                "logs_expiring_soon": stats.logs_expiring_soon,
                "most_shared_log": stats.most_shared_log,
                "total_shares": stats.total_shares,
                "storage_tier": stats.storage_tier
            }
            
            # Generate upgrade hints based on usage
            upgrade_hints = []
            if tier == "free":
                if stats.total_logs > 30:
                    upgrade_hints.append("🚀 You're an active user! Pro tier gives you 90-day retention.")
                if stats.total_shares > 10:
                    upgrade_hints.append("📊 Pro tier includes detailed sharing analytics!")
                if stats.logs_expiring_soon > 5:
                    upgrade_hints.append("⏰ Upgrade to Pro to keep your logs longer!")
            
            return CloudStatsResponse(
                success=True,
                stats=stats_dict,
                upgrade_hints=upgrade_hints
            )
            
        except Exception as e:
            logger.error(f"Error getting cloud stats: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get cloud stats: {str(e)}"
            )
    
    @app.post("/api/v1/cloud/cleanup")
    async def cleanup_expired_logs():
        """
        🧹 Clean up expired logs (automatic privacy protection).
        
        This runs automatically but can also be triggered manually.
        Like emptying your trash folder to free up space.
        """
        try:
            cleaned_count = await cloud_manager.cleanup_expired_logs()
            
            return JSONResponse({
                "success": True,
                "message": f"✅ Cleaned up {cleaned_count} expired logs",
                "logs_removed": cleaned_count
            })
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Cleanup failed: {str(e)}"
            )
    
    logger.info("🌤️ Cloud API routes added successfully!")
    return app

# Export the setup function
__all__ = ['setup_cloud_routes']