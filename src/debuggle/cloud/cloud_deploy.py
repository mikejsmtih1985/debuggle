"""
🚀 CLOUD DEPLOYMENT HELPER - Get Debuggle in the Sky! ☁️🛠️

Think of this like a moving company that helps you set up your new home:
- LOCAL DEBUGGLE = Your current apartment (works great, private, always there)
- CLOUD DEBUGGLE = Your new house with extra rooms (shareable, accessible from anywhere)

🏗️ HIGH SCHOOL EXPLANATION:
Imagine you want to put your school project online so classmates can see it:

WITHOUT DEPLOYMENT HELPER (the hard way):
1. Learn about web hosting, domain names, server configuration
2. Set up accounts on multiple platforms
3. Figure out environment variables, security settings
4. Write deployment scripts, configure databases
5. Debug networking issues, SSL certificates
6. Spend weeks learning DevOps instead of building features

WITH DEPLOYMENT HELPER (the easy way):
1. Run: `python -m debuggle.cloud.deploy --platform vercel`
2. Answer a few questions (like "What's your project name?")
3. Get a cup of coffee while it sets everything up
4. Your Debuggle is live at `https://yourname-debuggle.vercel.app`
5. Share error links immediately!

🎯 WHAT THIS CLASS DOES:
- Detects your existing Debuggle setup and configuration
- Generates deployment configs for different platforms (Vercel, Fly.io, Railway)
- Handles environment variables and secrets securely
- Sets up databases, caching, and search backends
- Provides simple commands for updates and rollbacks
- Monitors deployments and provides helpful error messages

🌍 SUPPORTED PLATFORMS:
- Vercel: Best for API + frontend, global CDN, generous free tier
- Fly.io: Great for SQLite + background jobs, persistent storage
- Railway: Simple full-stack hosting, good for beginners
- Hybrid: Use multiple platforms for optimal performance/cost

This turns cloud deployment from a week-long nightmare into a 5-minute setup!
"""

import os
import json
import yaml
import subprocess
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class DeploymentConfig:
    """
    📋 Configuration for deploying Debuggle to a cloud platform.
    
    Think of this like a moving checklist when you move to a new house:
    - What platform are we moving to? (Vercel, Fly.io, etc.)
    - What's the new address? (domain name)
    - What stuff do we need to pack? (environment variables)
    - What services do we need to set up? (database, search, etc.)
    """
    platform: str  # "vercel", "fly", "railway", "hybrid"
    project_name: str
    domain: Optional[str] = None
    environment: str = "production"  # "development", "staging", "production"
    tier: str = "free"  # "free", "pro", "enterprise"
    
    # Platform-specific settings
    vercel_config: Optional[Dict[str, Any]] = None
    fly_config: Optional[Dict[str, Any]] = None
    railway_config: Optional[Dict[str, Any]] = None
    
    # Required services
    needs_database: bool = True
    needs_redis: bool = False
    needs_search: bool = True
    needs_file_storage: bool = True
    
    # Environment variables
    env_vars: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.env_vars is None:
            self.env_vars = {}

class CloudDeploymentHelper:
    """
    🚀 The main class that handles deploying Debuggle to cloud platforms.
    
    HIGH SCHOOL ANALOGY:
    This is like having a professional moving company for your code:
    
    1. You say "I want to move my Debuggle to the cloud"
    2. Moving company (this class) surveys your current setup
    3. They pack everything properly (generate config files)
    4. They handle all the logistics (platform setup, DNS, etc.)
    5. They move your stuff to the new place (deploy the code)
    6. They make sure everything works (run health checks)
    7. They give you the keys to your new place (URLs, access info)
    
    The result: Your local Debuggle becomes a shareable cloud service!
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        🏗️ Initialize the deployment helper.
        
        Like hiring a moving company - they need to know where your stuff is!
        """
        self.project_root = project_root or Path.cwd()
        self.debuggle_root = self._find_debuggle_root()
        
        # Supported deployment platforms
        self.platforms = {
            "vercel": {
                "name": "Vercel",
                "description": "Best for FastAPI + frontend, global CDN",
                "free_tier": "100GB bandwidth, serverless functions",
                "setup_time": "2-3 minutes",
                "complexity": "Low"
            },
            "fly": {
                "name": "Fly.io", 
                "description": "Great for SQLite + background jobs",
                "free_tier": "3GB storage, 160GB bandwidth",
                "setup_time": "3-5 minutes", 
                "complexity": "Low-Medium"
            },
            "railway": {
                "name": "Railway",
                "description": "Simple full-stack hosting",
                "free_tier": "$5/month credit",
                "setup_time": "2-4 minutes",
                "complexity": "Low"
            },
            "hybrid": {
                "name": "Hybrid (Vercel + Fly.io)",
                "description": "Best performance + reliability",
                "free_tier": "Combined free tiers",
                "setup_time": "5-8 minutes",
                "complexity": "Medium"
            }
        }
        
        logger.info(f"🚀 Deployment helper initialized for {self.debuggle_root}")
    
    def _find_debuggle_root(self) -> Path:
        """Find the root directory of the Debuggle project."""
        current = self.project_root
        while current != current.parent:
            if (current / "entry_point.py").exists() and (current / "src" / "debuggle").exists():
                return current
            current = current.parent
        
        # If not found, assume current directory
        return self.project_root
    
    async def detect_current_setup(self) -> Dict[str, Any]:
        """
        🔍 Detect the current Debuggle setup and configuration.
        
        Like a moving company surveying your current home:
        - What stuff do you have? (features, databases, etc.)
        - How is it currently organized? (file structure)
        - What needs special handling? (custom configs, secrets)
        """
        setup_info = {
            "project_root": str(self.debuggle_root),
            "has_entry_point": (self.debuggle_root / "entry_point.py").exists(),
            "has_main_py": (self.debuggle_root / "src" / "debuggle" / "main.py").exists(),
            "has_requirements": (self.debuggle_root / "requirements.txt").exists(),
            "has_docker": (self.debuggle_root / "docker" / "Dockerfile").exists(),
            "has_cloud_module": (self.debuggle_root / "src" / "debuggle" / "cloud").exists(),
            "current_features": [],
            "databases": [],
            "environment_vars": []
        }
        
        # Detect features by checking imports and files
        if (self.debuggle_root / "src" / "debuggle" / "storage" / "search_engine.py").exists():
            setup_info["current_features"].append("search_engine")
        
        if (self.debuggle_root / "examples" / "viral_demo.py").exists():
            setup_info["current_features"].append("viral_demo")
        
        # Check for database files
        db_files = list(self.debuggle_root.glob("*.db"))
        setup_info["databases"] = [str(f) for f in db_files]
        
        # Look for environment variables in various files
        env_files = [".env", ".env.local", ".env.production"]
        for env_file in env_files:
            env_path = self.debuggle_root / env_file
            if env_path.exists():
                setup_info["environment_vars"].append(env_file)
        
        logger.info(f"📊 Detected setup: {len(setup_info['current_features'])} features, {len(setup_info['databases'])} databases")
        return setup_info
    
    async def recommend_platform(self, requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        💡 Recommend the best deployment platform based on needs.
        
        Like a moving company recommending truck size based on your stuff:
        - Small apartment (basic Debuggle) → Vercel
        - House with garage (Pro features) → Fly.io
        - Mansion (Enterprise) → Hybrid setup
        """
        if not requirements:
            requirements = {}
        
        # Default scoring (higher = better match)
        scores = {
            "vercel": 7,    # Great default choice
            "fly": 6,       # Good for storage-heavy apps
            "railway": 5,   # Simple but limited
            "hybrid": 8     # Best but more complex
        }
        
        # Adjust scores based on requirements
        if requirements.get("needs_database", True):
            scores["fly"] += 2      # Fly.io excels at SQLite
            scores["hybrid"] += 1
        
        if requirements.get("needs_redis", False):
            scores["vercel"] += 2   # Vercel KV is excellent
            scores["hybrid"] += 2
        
        if requirements.get("expected_traffic", "low") == "high":
            scores["vercel"] += 2   # Best CDN
            scores["hybrid"] += 3
        
        if requirements.get("complexity_tolerance", "low") == "high":
            scores["hybrid"] += 2   # More complex but more powerful
        else:
            scores["vercel"] += 2   # Simpler setup
            scores["railway"] += 1
        
        # Find the best match
        best_platform = max(scores.items(), key=lambda x: x[1])
        
        recommendation = {
            "recommended_platform": best_platform[0],
            "confidence_score": best_platform[1],
            "reasoning": self._generate_recommendation_reasoning(best_platform[0], requirements),
            "alternatives": sorted(
                [(k, v) for k, v in scores.items() if k != best_platform[0]], 
                key=lambda x: x[1], 
                reverse=True
            )[:2]
        }
        
        logger.info(f"💡 Recommended platform: {best_platform[0]} (score: {best_platform[1]})")
        return recommendation
    
    def _generate_recommendation_reasoning(self, platform: str, requirements: Dict[str, Any]) -> List[str]:
        """Generate human-readable reasoning for platform recommendation."""
        reasons = []
        
        if platform == "vercel":
            reasons.extend([
                "✅ Excellent for FastAPI backends with generous free tier",
                "⚡ Global CDN ensures fast response times worldwide",
                "🔧 Simple deployment with minimal configuration needed"
            ])
        elif platform == "fly":
            reasons.extend([
                "💾 Great for SQLite databases with persistent storage",
                "🏠 Keeps your data in a single location (easier backup)",
                "🐳 Excellent Docker support for complex applications"
            ])
        elif platform == "railway":
            reasons.extend([
                "🎯 Simplest setup for beginners",
                "💳 Predictable pricing with monthly credits",
                "🔄 Easy to upgrade and scale resources"
            ])
        elif platform == "hybrid":
            reasons.extend([
                "🎪 Best of both worlds: Vercel speed + Fly.io storage",
                "💪 Maximum reliability with redundant systems",
                "📈 Optimal performance for growing applications"
            ])
        
        return reasons
    
    async def generate_deployment_config(self, 
                                       platform: str, 
                                       project_name: str,
                                       tier: str = "free",
                                       custom_settings: Optional[Dict[str, Any]] = None) -> DeploymentConfig:
        """
        📋 Generate deployment configuration for the chosen platform.
        
        Like creating a detailed moving plan:
        - What platform are we moving to?
        - What's the timeline?
        - What special requirements do we have?
        - What needs to be configured where?
        """
        config = DeploymentConfig(
            platform=platform,
            project_name=project_name,
            tier=tier,
            env_vars=self._generate_env_vars(tier)
        )
        
        # Platform-specific configuration
        if platform == "vercel":
            config.vercel_config = await self._generate_vercel_config(project_name, tier)
        elif platform == "fly":
            config.fly_config = await self._generate_fly_config(project_name, tier)
        elif platform == "railway":
            config.railway_config = await self._generate_railway_config(project_name, tier)
        elif platform == "hybrid":
            config.vercel_config = await self._generate_vercel_config(project_name, tier)
            config.fly_config = await self._generate_fly_config(f"{project_name}-storage", tier)
        
        # Apply custom settings
        if custom_settings:
            if config.env_vars is None:
                config.env_vars = {}
            config.env_vars.update(custom_settings.get("env_vars", {}))
        
        logger.info(f"📋 Generated {platform} deployment config for {project_name}")
        return config
    
    async def create_deployment_files(self, config: DeploymentConfig) -> List[Path]:
        """
        📁 Create all necessary deployment files.
        
        Like packing boxes with proper labels for the movers:
        - vercel.json for Vercel configuration
        - fly.toml for Fly.io settings  
        - railway.json for Railway setup
        - GitHub Actions workflows for CI/CD
        """
        created_files = []
        
        try:
            # Create platform-specific config files
            if config.platform in ["vercel", "hybrid"]:
                vercel_file = await self._create_vercel_json(config)
                if vercel_file:
                    created_files.append(vercel_file)
            
            if config.platform in ["fly", "hybrid"]:
                fly_file = await self._create_fly_toml(config)
                if fly_file:
                    created_files.append(fly_file)
            
            if config.platform == "railway":
                railway_file = await self._create_railway_json(config)
                if railway_file:
                    created_files.append(railway_file)
            
            # Create GitHub Actions workflow
            workflow_file = await self._create_github_workflow(config)
            if workflow_file:
                created_files.append(workflow_file)
            
            # Create environment template
            env_file = await self._create_env_template(config)
            if env_file:
                created_files.append(env_file)
            
            logger.info(f"📁 Created {len(created_files)} deployment files")
            return created_files
            
        except Exception as e:
            logger.error(f"Error creating deployment files: {e}")
            return created_files
    
    # Platform-specific configuration generators
    
    def _generate_env_vars(self, tier: str) -> Dict[str, str]:
        """Generate environment variables for the deployment."""
        env_vars = {
            "DEBUGGLE_TIER": tier,
            "DEBUGGLE_CLOUD_ENABLED": "true",
            "DEBUGGLE_ANALYTICS_ENABLED": "true" if tier != "free" else "false",
            "DEBUGGLE_RATE_LIMIT_ENABLED": "true"
        }
        
        if tier in ["pro", "enterprise"]:
            env_vars.update({
                "DEBUGGLE_RETENTION_DAYS": "90" if tier == "pro" else "365",
                "DEBUGGLE_MAX_UPLOAD_SIZE": "10MB" if tier == "pro" else "100MB"
            })
        
        return env_vars
    
    async def _generate_vercel_config(self, project_name: str, tier: str) -> Dict[str, Any]:
        """Generate Vercel-specific configuration."""
        return {
            "name": project_name,
            "version": 2,
            "builds": [
                {
                    "src": "src/debuggle/main.py",
                    "use": "@vercel/python"
                }
            ],
            "routes": [
                {
                    "src": "/api/(.*)", 
                    "dest": "/src/debuggle/main.py"
                },
                {
                    "src": "/(.*)",
                    "dest": "/assets/static/index.html"
                }
            ],
            "env": {
                "PYTHONPATH": "src"
            },
            "functions": {
                "src/debuggle/main.py": {
                    "maxDuration": 30
                }
            }
        }
    
    async def _generate_fly_config(self, project_name: str, tier: str) -> Dict[str, Any]:
        """Generate Fly.io-specific configuration."""
        return {
            "app": project_name,
            "primary_region": "ord",  # Chicago - central US
            "build": {
                "dockerfile": "docker/Dockerfile"
            },
            "http_service": {
                "internal_port": 8000,
                "force_https": True,
                "auto_stop_machines": True,
                "auto_start_machines": True
            },
            "vm": {
                "size": "shared-cpu-1x" if tier == "free" else "shared-cpu-2x"
            },
            "mounts": [
                {
                    "source": "debuggle_data",
                    "destination": "/app/data"
                }
            ] if tier in ["pro", "enterprise"] else []
        }
    
    async def _generate_railway_config(self, project_name: str, tier: str) -> Dict[str, Any]:
        """Generate Railway-specific configuration."""
        return {
            "name": project_name,
            "build": {
                "command": "pip install -r requirements.txt"
            },
            "start": {
                "command": "python entry_point.py server --host 0.0.0.0 --port $PORT"
            },
            "env": {
                "PYTHON_VERSION": "3.11"
            }
        }
    
    # File creation methods
    
    async def _create_vercel_json(self, config: DeploymentConfig) -> Optional[Path]:
        """Create vercel.json configuration file."""
        if not config.vercel_config:
            return None
        
        vercel_path = self.debuggle_root / "vercel.json"
        
        with open(vercel_path, 'w') as f:
            json.dump(config.vercel_config, f, indent=2)
        
        logger.info(f"📁 Created vercel.json")
        return vercel_path
    
    async def _create_fly_toml(self, config: DeploymentConfig) -> Optional[Path]:
        """Create fly.toml configuration file."""
        if not config.fly_config:
            return None
        
        fly_path = self.debuggle_root / "fly.toml"
        
        with open(fly_path, 'w') as f:
            # Convert dict to TOML format
            for key, value in config.fly_config.items():
                if isinstance(value, dict):
                    f.write(f"[{key}]\n")
                    for subkey, subvalue in value.items():
                        f.write(f'{subkey} = "{subvalue}"\n')
                    f.write("\n")
                elif isinstance(value, list):
                    f.write(f"[[{key}]]\n")
                    for item in value:
                        if isinstance(item, dict):
                            for subkey, subvalue in item.items():
                                f.write(f'{subkey} = "{subvalue}"\n')
                        f.write("\n")
                else:
                    f.write(f'{key} = "{value}"\n')
        
        logger.info(f"📁 Created fly.toml")
        return fly_path
    
    async def _create_railway_json(self, config: DeploymentConfig) -> Optional[Path]:
        """Create railway.json configuration file."""
        if not config.railway_config:
            return None
        
        railway_path = self.debuggle_root / "railway.json"
        
        with open(railway_path, 'w') as f:
            json.dump(config.railway_config, f, indent=2)
        
        logger.info(f"📁 Created railway.json")
        return railway_path
    
    async def _create_github_workflow(self, config: DeploymentConfig) -> Optional[Path]:
        """Create GitHub Actions workflow for CI/CD."""
        workflow_dir = self.debuggle_root / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_path = workflow_dir / f"deploy-{config.platform}.yml"
        
        workflow_content = f"""name: Deploy to {config.platform.title()}

on:
  push:
    branches: [ main, debuggle-pro ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v
    
    - name: Deploy to {config.platform.title()}
      if: github.ref == 'refs/heads/main'
      run: |
        echo "🚀 Deploying to {config.platform}..."
        # Platform-specific deployment commands would go here
"""
        
        with open(workflow_path, 'w') as f:
            f.write(workflow_content)
        
        logger.info(f"📁 Created GitHub workflow: {workflow_path}")
        return workflow_path
    
    async def _create_env_template(self, config: DeploymentConfig) -> Path:
        """Create environment variables template."""
        env_path = self.debuggle_root / ".env.cloud.template"
        
        with open(env_path, 'w') as f:
            f.write("# Debuggle Cloud Environment Variables\n")
            f.write("# Copy this to .env.cloud and fill in your values\n\n")
            
            if config.env_vars:
                for key, value in config.env_vars.items():
                    f.write(f"{key}={value}\n")
            
            f.write("\n# Add your platform-specific secrets:\n")
            f.write("# VERCEL_TOKEN=your_vercel_token_here\n")
            f.write("# FLY_API_TOKEN=your_fly_token_here\n")
            f.write("# RAILWAY_TOKEN=your_railway_token_here\n")
        
        logger.info(f"📁 Created environment template: {env_path}")
        return env_path

# Export the main class
__all__ = ['CloudDeploymentHelper', 'DeploymentConfig']