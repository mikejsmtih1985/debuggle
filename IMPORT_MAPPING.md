# 🔄 **IMPORT MAPPING & PATH REFERENCE UPDATES**

## 📋 **Files Requiring Import Updates**

### **1. Entry Points (Critical - App Won't Start Without These)**

#### **entry_point.py** 
```python
# CURRENT (Line 191):
from src.debuggle.main import app

# NEW:
from src.debuggle.app_factory import create_app
app = create_app()
```

#### **debuggle_standalone.py**
```python  
# CURRENT (Line 41):
from src.debuggle.main import app as debuggle_app

# NEW:
from src.debuggle.app_factory import create_app
debuggle_app = create_app()
```

#### **src/debuggle/__init__.py**
```python
# CURRENT (Lines 22-23):
def get_app():
    from .main import app
    return app

# NEW:
def get_app():
    from .app_factory import create_app
    return create_app()
```

---

### **2. Test Files (20 Files - Must All Be Updated)**

All test files follow the same pattern:

#### **Pattern for ALL test files:**
```python
# CURRENT:
from src.debuggle.main import app

# NEW:  
from src.debuggle.app_factory import create_app
app = create_app()
```

#### **Specific Test Files to Update:**
1. `tests/test_main_comprehensive_new.py` (Line 19)
2. `tests/test_final_90_percent_push.py` (Line 76)
3. `tests/test_easy_coverage_boost.py` (Line 3)
4. `tests/test_final_hump.py` (Line 12)
5. `tests/test_100_percent_coverage.py` (Line 9)
6. `tests/test_final_coverage_push.py` (Line 8)
7. `tests/test_file_upload.py` (Line 6)
8. `tests/test_targeted_90_percent.py` (Line 21)
9. `tests/test_main_comprehensive.py` (Line 26)
10. `tests/test_dashboard_comprehensive_new.py` (Line 20)
11. `tests/test_minimal_coverage_push.py` (Line 16)
12. `tests/test_cloud_storage.py` (Line 435)
13. `tests/test_api.py` (Line 3)
14. `tests/test_coverage_boost_final.py` (Line 18)
15. `tests/test_api_coverage.py` (Line 7)

#### **Special Case - tests/test_minimal_coverage_push.py:**
```python
# CURRENT (Line 95):
import src.debuggle.main

# NEW:
import src.debuggle.app_factory  
# Then use create_app() where needed
```

#### **Special Case - tests/test_cloud_storage.py:**
```python
# CURRENT (Line 435):
import src.debuggle.main

# NEW:
import src.debuggle.app_factory
# Then use create_app() where needed
```

---

### **3. Internal Module Import Updates**

#### **New Models Structure Imports:**

**In API Route Files:**
```python
# CURRENT (main.py imports everything):
from .models import (
    AnalyzeRequest, AnalyzeResponse, AnalyzeMetadata,
    FileUploadResponse, FileUploadMetadata, LanguageEnum,
    HealthResponse, TiersResponse, TierFeature, ErrorResponse,
    # ... many more
)

# NEW (in api/routes/analysis.py):
from ...models.analysis import (
    AnalyzeRequest, 
    AnalyzeResponse,
    AnalyzeMetadata
)
from ...models.common import LanguageEnum, LogSeverity

# NEW (in api/routes/upload.py):  
from ...models.upload import (
    FileUploadResponse,
    FileUploadMetadata
)
from ...models.common import LanguageEnum

# NEW (in api/routes/dashboard.py):
from ...models.dashboard import (
    ChartDataRequest,
    ChartDataResponse, 
    DashboardRequest,
    DashboardResponse,
    SystemMetricsResponse
)
from ...models.common import TimeRangeAPI, ChartTypeAPI

# NEW (in api/routes/health.py):
from ...models.common import HealthResponse, ErrorResponse

# NEW (in api/routes/alerts.py):
from ...models.alerts import (
    AlertRuleRequest,
    AlertRuleResponse,
    AlertResponse,
    AlertStatsResponse
)
from ...models.common import AlertSeverityAPI, AlertChannelAPI
```

#### **Service Layer Imports:**
```python
# NEW (in services/analysis_service.py):
from ..core.processor import LogProcessor
from ..models.analysis import AnalyzeRequest, AnalyzeResponse
from ..storage import DatabaseManager

# NEW (in services/upload_service.py):
from ..models.upload import FileUploadResponse, FileUploadMetadata
from ..core.processor import LogProcessor
from ..storage import DatabaseManager

# NEW (in services/dashboard_service.py):
from ..dashboard import initialize_dashboard_engine
from ..models.dashboard import ChartDataRequest, DashboardResponse
from ..storage import DatabaseManager
```

#### **App Factory Imports:**
```python
# NEW (in app_factory.py):
from fastapi import FastAPI
from .config_v2 import settings
from .api.middleware import setup_middleware
from .api.routes import register_all_routes
from .dependencies import setup_dependencies
from .realtime import connection_manager, error_monitor
from .self_monitor import setup_self_monitoring
```

---

### **4. Route Registration Updates**

#### **New Route Structure:**
```python
# NEW (in api/routes/__init__.py):
from .analysis import router as analysis_router
from .upload import router as upload_router
from .dashboard import router as dashboard_router
from .realtime import router as realtime_router
from .alerts import router as alerts_router
from .ingestion import router as ingestion_router
from .health import router as health_router
from .info import router as info_router

def register_all_routes(app):
    """Register all API routes with the FastAPI app."""
    app.include_router(analysis_router, prefix="/api/v1", tags=["analysis"])
    app.include_router(upload_router, prefix="/api/v1", tags=["upload"])
    app.include_router(dashboard_router, prefix="/api/v1", tags=["dashboard"])
    app.include_router(realtime_router, prefix="/ws", tags=["realtime"])
    app.include_router(alerts_router, prefix="/api/v1", tags=["alerts"])
    app.include_router(ingestion_router, prefix="/api/v1", tags=["ingestion"])
    app.include_router(health_router, tags=["health"])
    app.include_router(info_router, prefix="/api/v1", tags=["info"])
```

---

### **5. Dependency Injection Updates**

#### **New Dependencies Structure:**
```python
# NEW (in dependencies.py):
from functools import lru_cache
from .core.processor import LogProcessor
from .storage import DatabaseManager, SearchManager, RetentionManager
from .alerting import AlertManager
from .services.analysis_service import AnalysisService
from .services.upload_service import UploadService
from .services.dashboard_service import DashboardService

@lru_cache()
def get_processor():
    """Get LogProcessor instance (singleton)."""
    return LogProcessor()

@lru_cache()
def get_database_manager():
    """Get DatabaseManager instance (singleton)."""
    return DatabaseManager("logs.db")

@lru_cache() 
def get_analysis_service():
    """Get AnalysisService instance (singleton)."""
    return AnalysisService()

# Usage in route files:
from fastapi import Depends
from ...dependencies import get_analysis_service
from ...services.analysis_service import AnalysisService

@router.post("/analyze")
async def analyze_log(
    request: AnalyzeRequest,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    return await analysis_service.analyze_log(request)
```

---

### **6. Cross-Module Reference Updates**

#### **Internal Import Updates Within Routes:**
```python  
# CURRENT (in main.py - everything is in one file):
processor = LogProcessor()
database_manager = DatabaseManager("logs.db")
# Direct usage in same file

# NEW (in api/routes/analysis.py):
from ...dependencies import get_processor, get_database_manager
from ...services.analysis_service import AnalysisService

# Use dependency injection instead of direct instantiation
```

#### **WebSocket Handler Updates:**
```python
# CURRENT (in main.py WebSocket endpoint):
@app.websocket("/ws/errors")
async def websocket_endpoint(websocket: WebSocket):
    # Handler code here

# NEW (in api/routes/realtime.py):
@router.websocket("/errors")  # Note: prefix "/ws" added by router registration
async def websocket_endpoint(websocket: WebSocket):
    # Same handler code, but in dedicated file
```

---

### **7. Static File and Template Updates**

#### **Static File Mounting:**
```python
# CURRENT (in main.py):
static_dir = "assets/static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# NEW (in app_factory.py):
def setup_static_files(app):
    """Set up static file serving."""
    static_dir = "assets/static"
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
```

#### **HTML Response Updates:**
```python
# CURRENT (in main.py root endpoint):
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("assets/static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

# NEW (in api/routes/info.py):
@router.get("/", response_class=HTMLResponse)
async def root():
    with open("assets/static/index.html", "r") as f:
        return HTMLResponse(content=f.read())
```

---

## 🔧 **AUTOMATED UPDATE SCRIPT**

### **Import Update Automation:**
```python
#!/usr/bin/env python3
"""
Automated script to update all import statements during refactoring.
Run this after creating the new structure to update all references.
"""

import os
import re
from pathlib import Path

def update_main_imports():
    """Update all imports of main.py to use app_factory.py"""
    
    # Files to update
    files_to_update = [
        "entry_point.py",
        "debuggle_standalone.py", 
        "src/debuggle/__init__.py",
        # Add all test files
        "tests/test_main_comprehensive_new.py",
        "tests/test_final_90_percent_push.py",
        # ... add all test files from the list above
    ]
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Replace main.py imports
            content = re.sub(
                r'from src\.debuggle\.main import app',
                'from src.debuggle.app_factory import create_app\napp = create_app()',
                content
            )
            
            # Handle special cases
            content = re.sub(
                r'import src\.debuggle\.main',
                'import src.debuggle.app_factory',
                content  
            )
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Updated {file_path}")

if __name__ == "__main__":
    update_main_imports()
```

---

## ✅ **VALIDATION CHECKLIST**

After updates, verify:

### **Import Validation:**
- [ ] All test files import `create_app()` correctly
- [ ] Entry points use new app factory  
- [ ] Package `__init__.py` exports work
- [ ] New model imports resolve correctly
- [ ] Service dependencies inject properly

### **Functionality Validation:**  
- [ ] FastAPI app starts without errors
- [ ] All API endpoints respond correctly
- [ ] WebSocket connections work
- [ ] File uploads process correctly
- [ ] Database operations function
- [ ] CLI tools work unchanged

### **Integration Validation:**
- [ ] VS Code extension connects properly
- [ ] Standalone distribution works
- [ ] Docker builds succeed
- [ ] All tests pass

This comprehensive mapping ensures **zero breaking changes** during the refactoring process! 🎯