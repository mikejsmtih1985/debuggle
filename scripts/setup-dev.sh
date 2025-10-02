#!/bin/bash

#
# 🏗️ DEBUGGLE DEVELOPMENT WORKBENCH SETUP - Automated Environment Builder
# ========================================================================
#
# This shell script is like having a skilled technician who can set up a
# complete development workshop from scratch, installing all the tools,
# organizing the workspace, and ensuring everything is ready for productive work.
#
# 🏆 HIGH SCHOOL EXPLANATION:
# Think of this like setting up a new art studio, music studio, or workshop:
# 1. Check you have the right basic tools (Python version check)
# 2. Set up your dedicated workspace (virtual environment)
# 3. Install all specialized equipment (dependencies)
# 4. Create necessary storage areas (directories)
# 5. Set up your preferences and settings (configuration files)
#
# Instead of doing all these steps manually every time someone joins the
# project, this script automates the entire setup process. New developers
# can run one command and have a fully configured development environment.
#
# EDUCATIONAL METAPHORS USED:
# 🏗️ Construction & Setup - Building workspaces and installing equipment
# 🔧 Workshop Organization - Tool management and workspace preparation
# 📋 Installation Procedures - Following setup checklists and protocols
# ⚡ Automation Systems - Reducing manual work through scripting
#

# 🛡️ SAFETY PROTOCOL - Exit immediately if any step fails
# This is like having an emergency stop button that halts the entire
# setup process if something goes wrong, preventing partial installations
set -e

# 📢 SETUP INITIATION ANNOUNCEMENT
echo "🚀 Setting up Debuggle development environment..."

#
# 🔍 FOUNDATION INSPECTION - Verifying we have the right Python version
# =====================================================================
#
# This step is like checking that you have the right power tools before
# starting a construction project. Different Python versions are like
# different tool models - our project needs specific capabilities.
#
echo "📋 Checking Python version..."
python3 --version  # 📊 Display Python version for verification and troubleshooting

#
# 🏠 ISOLATED WORKSPACE CREATION - Setting up virtual environment
# ===============================================================
#
# A virtual environment is like having a separate, clean workshop for each
# project. This prevents different projects from interfering with each other's
# tools and materials.
#
# 🏆 HIGH SCHOOL EXPLANATION:
# Think of this like having separate art supply boxes for different classes:
# - Your painting supplies don't get mixed up with your sculpture tools
# - Each project has exactly the materials it needs
# - You can work on multiple projects without conflicts
# - If one project's supplies get messy, it doesn't affect others
#
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv  # 📦 Create isolated Python environment in 'venv' folder
fi

#
# ⚡ WORKSPACE ACTIVATION - Switching to our project-specific environment
# ======================================================================
#
# This is like walking into your dedicated workshop and turning on all the
# lights and equipment. Everything we do after this point will use our
# project-specific tools and settings.
#
echo "⚡ Activating virtual environment..."
source venv/bin/activate  # 🔌 Switch to our isolated Python environment

#
# 🔧 TOOL MAINTENANCE - Ensuring we have the latest package installer
# ===================================================================
#
# This is like making sure your toolbox has the latest, most reliable tools
# before starting work. pip is Python's "tool installer" - keeping it updated
# ensures smooth installation of other packages.
#
echo "📦 Upgrading pip..."
pip install --upgrade pip  # ⬆️ Update package installer to latest version

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p logs

# Set permissions
echo "🔐 Setting permissions..."
chmod 755 uploads logs

# Check if everything is working
echo "🧪 Testing installation..."
python3 -c "from src.debuggle.main import app; print('✅ Import successful')"

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run: source venv/bin/activate"
echo "3. Run: uvicorn app.main:app --reload"
echo "4. Open: http://localhost:8000"
echo ""