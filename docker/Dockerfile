#
# 📦 DEBUGGLE SHIPPING CONTAINER - Universal Software Packaging System
# ====================================================================
#
# This Dockerfile is like a detailed instruction manual for creating a
# standardized "shipping container" that can run our software anywhere
# in the world, regardless of the local environment.
#
# 🏆 HIGH SCHOOL EXPLANATION:
# Think of Docker like the shipping container revolution in global trade.
# Before containers, shipping was chaotic - different ports, different
# loading systems, different standards. Containers standardized everything.
#
# Similarly, before Docker, software deployment was messy:
# - "It works on my computer" - but not on the server
# - Different versions of libraries on different systems  
# - Complex setup instructions that break easily
#
# Docker creates a "container" that includes everything needed to run
# our software: the operating system, libraries, dependencies, and our code.
# It's like shipping a complete, ready-to-run computer instead of just software.
#
# EDUCATIONAL METAPHORS USED:
# 📦 Shipping & Logistics - Containers and standardized packaging
# 🏭 Manufacturing - Assembly line instructions and quality control
# 🏗️ Construction - Building from foundation up with proper materials
# 📋 Recipe Following - Step-by-step cooking/baking instructions
#

#
# 🧱 FOUNDATION SELECTION - Choosing our base operating system
# ===========================================================
#
# This is like choosing the foundation for a house. Python:3.11-slim is
# a pre-built "foundation" that includes a minimal Linux system with
# Python 3.11 already installed and configured properly.
#
# The "slim" version is like choosing an efficient apartment layout - 
# it has everything we need but removes unnecessary extras to save space.
#
FROM python:3.11-slim

#
# 🏠 WORKSPACE SETUP - Creating our application's home directory
# =============================================================
#
# This sets up the main folder where our application will live inside
# the container, like designating the main room in an apartment where
# all the important stuff goes.
#
WORKDIR /app

#
# ⚙️ ENVIRONMENT CONFIGURATION - Setting up the operating environment
# ===================================================================
#
# These environment variables configure how Python behaves in our container,
# like setting the thermostat, lighting, and ventilation in a workspace
# to create optimal conditions for productivity.
#
ENV PYTHONDONTWRITEBYTECODE=1 \    # 🚫 Don't create .pyc files (like temp files) - keeps container clean
    PYTHONUNBUFFERED=1 \           # 📺 See output immediately - like live TV vs recorded
    PYTHONPATH=/app                # 🗺️ Tell Python where to find our code - like setting GPS home address

#
# 🔧 TOOLBOX INSTALLATION - Setting up essential build tools
# ==========================================================
#
# This step installs the basic tools our software needs to compile and
# run properly, like stocking a workshop with essential tools before
# starting a complex project.
#
# 🏆 HIGH SCHOOL EXPLANATION:
# Think of this like setting up a workshop or garage:
# 1. Update the tool catalog (apt-get update) - like checking what's available
# 2. Install specific tools (gcc, g++) - like buying a drill and saw
# 3. Clean up packaging (rm -rf) - like throwing away the tool boxes
#
# The tools we're installing:
# - gcc: C compiler - like a basic drill for simple jobs
# - g++: C++ compiler - like an advanced drill for complex materials
#
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \                           # 🔨 C compiler for building Python extensions
        g++ \                           # 🔧 C++ compiler for advanced libraries
        && rm -rf /var/lib/apt/lists/*  # 🧹 Clean up package cache to keep container small

#
# 📋 DEPENDENCY BLUEPRINT - Copying our requirements list first
# ============================================================
#
# We copy the requirements.txt file before copying our main code because
# Docker has a smart caching system. This is like preparing your shopping
# list before going to multiple stores - if the list doesn't change,
# you don't need to shop again.
#
# This optimization means if we change our code but not our dependencies,
# Docker can skip reinstalling all the libraries, making builds much faster.
#
COPY requirements.txt .

#
# 📦 DEPENDENCY INSTALLATION - Installing all required Python libraries
# =====================================================================
#
# This is like going to a specialty store and buying all the specific
# tools and materials your project needs, following your shopping list
# exactly to ensure you have everything required.
#
# 🏆 HIGH SCHOOL EXPLANATION:
# Think of this like getting ready for a complex school project:
# 1. Update your package manager (upgrade pip) - like updating your app store
# 2. Install all libraries from requirements.txt - like buying all supplies from your list
# 3. Use --no-cache-dir - like not keeping shopping bags (saves space)
#
RUN pip install --no-cache-dir --upgrade pip \           # 📈 Get the latest package installer
    && pip install --no-cache-dir -r requirements.txt   # 📦 Install all our Python dependencies

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .

# Install the package
RUN pip install --no-cache-dir -e .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app

#
# 👤 SECURITY CHECKPOINT - Switching to non-privileged crew member
# ==============================================================
#
# 🏆 HIGH SCHOOL EXPLANATION:
# This is like switching from the ship captain to a regular crew member
# before the ship starts its journey. In computing, we don't want our
# application running with "superuser" powers (like being the captain)
# because if something goes wrong, it could take over the whole system.
# 
# Instead, we switch to a regular user account that can only do what
# it needs to do - like a crew member who can work on the ship but
# can't change the navigation or engine settings.
#
USER appuser

#
# 🚪 PORT ANNOUNCEMENT - Opening the shipping dock for deliveries  
# =============================================================
#
# 🏆 HIGH SCHOOL EXPLANATION:
# This tells Docker "our application will be listening on port 8000"
# like putting up a sign that says "Deliveries accepted at Dock 8000".
#
# Think of ports like numbered docks at a shipping port. When other
# services want to talk to our application, they know to send their
# messages to "dock 8000" on our container ship.
#
EXPOSE 8000

#
# 🏥 HEALTH MONITORING - Installing the ship's medical system
# =========================================================
#
# 🏆 HIGH SCHOOL EXPLANATION:
# This sets up an automatic health check system, like having a ship's
# doctor who checks on the crew every 30 seconds. If our application
# stops responding (like if the crew gets sick), Docker will know
# something is wrong and can take action.
#
# The health check works by:
# 1. Every 30 seconds, send a "ping" to our application
# 2. Wait up to 30 seconds for a response  
# 3. If it fails 3 times in a row, mark the container as "unhealthy"
# 4. This allows Docker to restart the container or alert monitoring systems
#
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

#
# 🚀 LAUNCH SEQUENCE - Starting the application engines
# ====================================================
#
# 🏆 HIGH SCHOOL EXPLANATION:
# This is the final command that actually starts our application, like
# turning the key to start a ship's engines. When Docker runs our container,
# this is the command it will execute.
#
# Breaking down the command:
# • uvicorn = The web server engine (like the ship's engine)
# • src.debuggle.main:app = The location of our application (like the ship's bridge)
# • --host 0.0.0.0 = Listen on all network interfaces (accept visitors from any dock)
# • --port 8000 = Use port 8000 (the same dock we announced above)
#
# This command will keep running until the container is stopped, just like
# how a ship's engines keep running until the captain orders them to stop.
#
CMD ["uvicorn", "src.debuggle.main:app", "--host", "0.0.0.0", "--port", "8000"]