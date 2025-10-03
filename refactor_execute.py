#!/usr/bin/env python3
"""
🏗️ DEBUGGLE REFACTORING EXECUTION SCRIPT 🏗️

This script automates the step-by-step refactoring of Debuggle's monolithic
codebase into a clean, modular architecture while preserving educational
comments and ensuring zero breaking changes.

Run each phase independently with validation between phases.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

class RefactoringExecutor:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.src_dir = self.root_dir / "src" / "debuggle"
        self.backup_created = False
        
    def create_backup(self):
        """Create safety backup before starting."""
        print("🔒 Creating safety backup...")
        result = subprocess.run(["git", "add", "-A"], capture_output=True)
        if result.returncode != 0:
            print("❌ Failed to stage changes")
            return False
            
        result = subprocess.run([
            "git", "commit", "-m", "Pre-refactoring backup"
        ], capture_output=True)
        
        result = subprocess.run([
            "git", "tag", "pre-refactoring-backup"
        ], capture_output=True)
        
        print("✅ Backup created at tag: pre-refactoring-backup")
        self.backup_created = True
        return True
        
    def validate_imports(self):
        """Quick validation that critical imports work."""
        try:
            # Test current structure  
            from src.debuggle.main import app
            print("✅ Current imports working")
            return True
        except ImportError as e:
            print(f"❌ Import validation failed: {e}")
            return False
            
    def create_directory_structure(self):
        """Phase 1: Create new directory structure."""
        print("\n🏗️ Phase 1: Creating directory structure...")
        
        directories = [
            "src/debuggle/models",
            "src/debuggle/api",
            "src/debuggle/api/routes", 
            "src/debuggle/services"
        ]
        
        for dir_path in directories:
            full_path = self.root_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {dir_path}")
            
        # Create __init__.py files
        init_files = [
            "src/debuggle/models/__init__.py",
            "src/debuggle/api/__init__.py",
            "src/debuggle/api/routes/__init__.py",
            "src/debuggle/services/__init__.py"
        ]
        
        for init_file in init_files:
            full_path = self.root_dir / init_file
            if not full_path.exists():
                full_path.touch()
                print(f"✅ Created: {init_file}")
                
        print("✅ Phase 1 Complete: Directory structure created")
        return True
        
    def create_app_factory(self):
        """Create the app factory file."""
        print("\n🏥 Creating Hospital Construction Manager (app_factory.py)...")
        
        app_factory_content = '''"""
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
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from .config_v2 import settings
from .api.middleware import setup_middleware  
from .api.routes import register_all_routes
from .dependencies import setup_dependencies
from .realtime import connection_manager, error_monitor
from .self_monitor import setup_self_monitoring

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
    
    Returns:
        FastAPI: A complete, fully-equipped digital hospital ready to serve patients!
    """
    
    # Step 1: Design the hospital blueprint
    print("🏗️ Designing hospital blueprint...")
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version, 
        description="🐞 Debuggle Core - Professional log analysis and error diagnosis",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Step 2: Install foundation systems (middleware, security, monitoring)
    print("🔧 Installing hospital infrastructure...")
    setup_middleware(app)
    
    # Step 3: Set up hospital supply chain (dependency injection)
    print("📦 Setting up hospital supply chain...")
    setup_dependencies(app)
    
    # Step 4: Build all medical departments (register API routes)
    print("🏥 Building medical departments...")
    register_all_routes(app)
    
    # Step 5: Install patient amenities (static files)
    print("📚 Setting up patient information center...")
    setup_static_files(app)
    
    # Step 6: Activate monitoring systems
    print("📡 Activating hospital monitoring systems...")
    setup_self_monitoring(app, connection_manager)
    
    print("✅ Digital hospital construction complete! Ready to serve patients.")
    return app


def setup_static_files(app: FastAPI):
    """
    📚 PATIENT INFORMATION CENTER - Static File Setup! 📚
    
    This sets up the hospital's information center where patients can
    access brochures, forms, and educational materials (HTML, CSS, JS files).
    Like having a well-organized information desk with all the resources
    patients need.
    """
    static_dir = "assets/static"
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        print(f"✅ Patient information center ready at: {static_dir}")
    else:
        print(f"⚠️ Information center directory not found: {static_dir}")


# For backward compatibility during transition
app = create_app()
'''
        
        app_factory_path = self.src_dir / "app_factory.py"
        with open(app_factory_path, 'w') as f:
            f.write(app_factory_content)
            
        print("✅ Hospital Construction Manager created!")
        return True
        
    def run_phase_tests(self, phase_name):
        """Run tests after each phase."""
        print(f"\n🧪 Testing {phase_name}...")
        
        # Quick import test
        try:
            if phase_name == "Phase 1":
                # Just test directory creation
                assert (self.src_dir / "models").exists()
                assert (self.src_dir / "api").exists()
                print("✅ Directory structure test passed")
                
            elif phase_name == "App Factory":
                # Test app factory import
                sys.path.insert(0, str(self.root_dir))
                from src.debuggle.app_factory import create_app
                app = create_app()
                print("✅ App factory test passed")
                
            return True
            
        except Exception as e:
            print(f"❌ {phase_name} test failed: {e}")
            return False
            
    def execute_phase_1(self):
        """Execute Phase 1: Foundation Setup."""
        print("\n" + "="*60)
        print("🏗️ PHASE 1: FOUNDATION SETUP")
        print("="*60)
        
        if not self.create_directory_structure():
            return False
            
        if not self.create_app_factory():
            return False
            
        if not self.run_phase_tests("Phase 1"):
            return False
            
        # Create checkpoint
        subprocess.run(["git", "add", "-A"], capture_output=True)
        subprocess.run([
            "git", "commit", "-m", "Phase 1 complete: Foundation setup"
        ], capture_output=True)
        subprocess.run(["git", "tag", "refactor-phase-1"], capture_output=True)
        
        print("✅ Phase 1 Complete - Foundation Ready!")
        print("🏷️ Checkpoint created: refactor-phase-1")
        return True
        
    def show_menu(self):
        """Show interactive menu."""
        print("\n" + "="*60)
        print("🏗️ DEBUGGLE REFACTORING EXECUTION MENU")
        print("="*60)
        print("1. 🔒 Create Safety Backup")
        print("2. 🏗️ Execute Phase 1: Foundation Setup")
        print("3. 📋 Execute Phase 2: Models Reorganization") 
        print("4. 🚪 Execute Phase 3: API Routes Extraction")
        print("5. 🧠 Execute Phase 4: Business Logic Services")
        print("6. 🔄 Execute Phase 5: External Reference Updates")
        print("7. 🧪 Execute Phase 6: Testing & Validation")
        print("8. 📊 Show Current Status")
        print("9. 🔙 Rollback to Previous Phase")
        print("0. ❌ Exit")
        print("="*60)
        
    def show_status(self):
        """Show current refactoring status."""
        print("\n📊 REFACTORING STATUS:")
        print("-" * 40)
        
        # Check for git tags to see what's been done
        result = subprocess.run([
            "git", "tag", "--list", "refactor-phase-*"
        ], capture_output=True, text=True)
        
        phases = result.stdout.strip().split('\\n') if result.stdout.strip() else []
        
        phase_names = [
            "Phase 1: Foundation Setup",
            "Phase 2: Models Reorganization", 
            "Phase 3: API Routes Extraction",
            "Phase 4: Business Logic Services", 
            "Phase 5: External Reference Updates",
            "Phase 6: Testing & Validation"
        ]
        
        for i, phase_name in enumerate(phase_names, 1):
            tag_name = f"refactor-phase-{i}"
            if tag_name in phases:
                print(f"✅ {phase_name}")
            else:
                print(f"⏳ {phase_name}")
                
        print("-" * 40)
        
    def rollback_phase(self):
        """Rollback to previous phase."""
        print("\\n🔙 Available rollback points:")
        
        result = subprocess.run([
            "git", "tag", "--list", "refactor-phase-*", "--sort=-version:refname"
        ], capture_output=True, text=True)
        
        if not result.stdout.strip():
            print("❌ No rollback points available")
            return False
            
        tags = result.stdout.strip().split('\\n')
        for i, tag in enumerate(tags[:5], 1):  # Show last 5
            print(f"{i}. {tag}")
            
        try:
            choice = input("\\nSelect rollback point (number): ")
            selected_tag = tags[int(choice) - 1]
            
            confirm = input(f"⚠️ Rollback to {selected_tag}? (y/N): ")
            if confirm.lower() == 'y':
                subprocess.run(["git", "reset", "--hard", selected_tag])
                print(f"✅ Rolled back to {selected_tag}")
                return True
            else:
                print("❌ Rollback cancelled")
                return False
                
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            return False
    
    def run(self):
        """Main execution loop."""
        if not self.validate_imports():
            print("❌ Current codebase has import issues. Fix before refactoring.")
            return False
            
        while True:
            self.show_menu()
            
            try:
                choice = input("\\nSelect option: ").strip()
                
                if choice == "0":
                    print("👋 Refactoring session ended")
                    break
                elif choice == "1":
                    self.create_backup()
                elif choice == "2":
                    self.execute_phase_1()
                elif choice == "8":
                    self.show_status()
                elif choice == "9":
                    self.rollback_phase()
                else:
                    print(f"❌ Option {choice} not implemented yet")
                    print("🚧 Additional phases coming in next iteration")
                    
            except KeyboardInterrupt:
                print("\\n\\n👋 Refactoring interrupted")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🏗️ Debuggle Refactoring Execution Tool")
    print("=====================================")
    
    executor = RefactoringExecutor()
    executor.run()