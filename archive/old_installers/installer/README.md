# Debuggle One-Click Installer System

## 🎯 Vision: "It Just Works" Experience

The new Debuggle installer transforms installation from a complex multi-step process into a single command that handles everything automatically. No matter your environment - WSL, Docker, Cloud, local machine - Debuggle detects and configures everything perfectly.

## 🤖 Meet Buggle - Your AI Assistant

Buggle is Debuggle's friendly AI companion who helps with installation, troubleshooting, and debugging. He can work with multiple AI providers (OpenAI, Anthropic, Google, local models) or use smart rule-based responses when AI isn't available.

## ✨ Key Features

### 🔍 Intelligent Environment Detection
- **Auto-detects**: WSL, Docker, AWS, GCP, Azure, Codespaces, Gitpod, Replit
- **Platform-aware**: Windows, macOS, Linux with appropriate package managers
- **IDE integration**: VS Code, JetBrains IDEs, Vim/Neovim detection
- **Development context**: Local, remote, containerized environments

### 🚀 Zero-Configuration Setup
- **Dependency management**: Auto-installs Python, Node.js, VS Code if needed
- **VS Code integration**: Automatic extension installation and workspace configuration
- **Workspace setup**: Creates optimal `.vscode/` settings and launch configurations
- **Path handling**: Correctly handles WSL/Windows path differences

### 🤖 Buggle AI Assistance
- **Smart troubleshooting**: Environment-specific guidance when issues occur
- **GitHub integration**: Auto-creates detailed support issues for edge cases
- **Multi-provider support**: Works with OpenAI, Anthropic, Google AI, or local models
- **Fallback responses**: Intelligent rule-based help when AI isn't available

### 🌐 Beautiful Web Interface
- **Real-time progress**: Live updates during installation
- **Interactive configuration**: Choose features and settings visually
- **Mobile-friendly**: Works on tablets and phones
- **Offline capable**: Runs locally after initial download

## 🚀 Installation Methods

### Method 1: One-Line Install (Recommended)
```bash
# Download and run in one command
curl -fsSL https://raw.githubusercontent.com/mikejsmtih1985/debuggle/main/install.py | python3

# Or with wget
wget -qO- https://raw.githubusercontent.com/mikejsmtih1985/debuggle/main/install.py | python3
```

### Method 2: Download First, Then Run
```bash
# Download installer
wget https://raw.githubusercontent.com/mikejsmtih1985/debuggle/main/install.py

# Run with options
python3 install.py --web              # Web interface
python3 install.py --silent           # Silent installation
python3 install.py --vscode-only      # VS Code integration only
```

### Method 3: Web-Based Installer
```bash
# Launch beautiful web installer
python3 install.py --web

# Then visit http://localhost:8080
```

### Method 4: From Local Repository
```bash
# If you already have the code
python3 install.py --local /path/to/debuggle
```

## 🎮 Usage Examples

### Basic Installation
```bash
# Detects environment and installs everything
python3 install.py
```

### Custom Workspace
```bash
# Install in specific project directory
python3 install.py --workspace ~/my-project
```

### Silent Installation for CI/CD
```bash
# Unattended installation with defaults
python3 install.py --silent --no-browser
```

### VS Code Only
```bash
# Just set up VS Code integration
python3 install.py --vscode-only
```

### Advanced Configuration
```bash
# Custom port, no shortcuts, auto-start enabled
python3 install.py --custom-port 3000 --no-shortcut --auto-start
```

## 🏗️ Architecture

### Core Components

#### 1. Universal Installer (`install.py`)
- Entry point that can be downloaded and run from anywhere
- Handles downloading, extraction, and setup of Debuggle
- Provides unified CLI interface with all options

#### 2. Environment Detection (`one_click_install.py`)
- **EnvironmentDetector**: Intelligent system analysis
- **SystemInfo**: Comprehensive environment data structure
- **DependencyManager**: Smart package installation

#### 3. Web Interface (`web_installer.py`)
- **FastAPI-based**: Modern async web framework
- **WebSocket updates**: Real-time installation progress
- **Responsive design**: Works on all devices
- **Interactive configuration**: Visual option selection

#### 4. GitHub Integration (`github_support.py`)
- **Issue auto-creation**: Detailed bug reports for edge cases
- **Smart troubleshooting**: Environment-specific guidance
- **Community learning**: Improves detection over time

### Environment Detection Matrix

| Environment | Detection Method | Package Manager | Special Handling |
|------------|------------------|-----------------|------------------|
| **WSL** | `/proc/version` + env vars | `apt`/`yum` | Remote-WSL extension |
| **Docker** | `/.dockerenv` file | Container PM | Volume persistence |
| **Codespaces** | `CODESPACES` env var | `apt` | Port forwarding setup |
| **Gitpod** | `GITPOD_WORKSPACE_ID` | `apt` | Prebuilt devcontainer |
| **AWS EC2** | Metadata endpoint | `yum`/`apt` | Security group config |
| **macOS** | `platform.system()` | `brew` | Homebrew installation |
| **Windows** | `platform.system()` | `choco`/manual | WSL vs native detection |

### VS Code Integration Pipeline

1. **Detection Phase**
   ```python
   # Check if VS Code is available
   has_vscode = detect_vscode()
   if not has_vscode:
       install_vscode_via_package_manager()
   ```

2. **Extension Installation**
   ```python
   # Build and install extension
   subprocess.run(['npm', 'install'], cwd='vscode-extension/')
   subprocess.run(['npm', 'run', 'compile'], cwd='vscode-extension/')
   subprocess.run(['code', '--install-extension', extension_path])
   ```

3. **Workspace Configuration**
   ```python
   # Create .vscode/settings.json
   settings = {
       "python.defaultInterpreterPath": "./.venv/bin/python",
       "debuggle.autoStart": True,
       "debuggle.port": 8000
   }
   ```

4. **Launch Configuration**
   ```python
   # Create .vscode/launch.json
   launch_config = {
       "configurations": [{
           "name": "Launch Debuggle Server",
           "type": "python",
           "program": "entry_point.py",
           "args": ["server"]
       }]
   }
   ```

## 🔧 Configuration Options

### Installation Modes
- `--web`: Launch web-based installer interface
- `--silent`: Unattended installation with sensible defaults
- `--vscode-only`: Only configure VS Code integration

### Feature Toggles
- `--no-vscode`: Skip VS Code integration entirely
- `--no-deps`: Skip automatic dependency installation
- `--no-workspace`: Skip workspace configuration
- `--no-shortcut`: Skip desktop shortcut creation
- `--no-browser`: Don't auto-open browser (web mode)

### Customization
- `--workspace PATH`: Install in specific directory
- `--custom-port PORT`: Use custom port for Debuggle server
- `--port PORT`: Custom port for web installer
- `--auto-start`: Enable auto-start on system boot

### Development Options
- `--local PATH`: Use local Debuggle directory
- `--target PATH`: Custom installation target

## 🚨 Error Handling & Support

### Automatic Issue Creation
When the installer encounters an unsupported environment:

1. **System Analysis**: Collects comprehensive environment data
2. **GitHub Issue**: Auto-creates detailed issue with:
   - Platform and architecture details
   - Environment detection results
   - Error logs and stack traces
   - Suggested implementation priority
   - Implementation checklist for developers

3. **Troubleshooting**: Provides immediate workarounds:
   - Environment-specific installation steps
   - Manual configuration guides
   - Alternative installation methods

### Example Auto-Generated Issue (via Buggle)
```markdown
## [Auto-Install Support] docker - linux

**Configuration Hash:** `a1b2c3d4`
**Environment Type:** docker
**Platform:** linux
**Buggle Analysis:** Advanced containerized environment detected

### System Information
- **Python Version:** 3.9.2
- **Package Manager:** apt
- **Shell:** bash

### Error Details
- Failed to install Node.js via apt
- VS Code not available in container
- WebSocket connectivity issues

### Buggle's Suggested Implementation
**🔥 HIGH PRIORITY** - Popular containerized workflow

### Implementation Checklist
- [ ] Create Docker-specific detection logic
- [ ] Implement container-aware dependency installation
- [ ] Add volume persistence configuration
- [ ] Test with common Docker images
```

## 🎯 Success Metrics

### User Experience Goals
- **Zero manual steps** for 90% of installations
- **< 3 minutes** end-to-end installation time
- **Single command** works across all major environments
- **Automatic recovery** from common failure scenarios

### Technical Objectives
- **Environment coverage**: Support 15+ environment types
- **Dependency resolution**: Handle version conflicts automatically
- **Integration quality**: VS Code works immediately after install
- **Failure recovery**: Auto-create GitHub issues for edge cases

## 🔮 Future Enhancements

### Phase 2: Advanced Buggle Features
- **Voice guidance**: Audio instructions for accessibility
- **Video tutorials**: Generated setup videos for complex scenarios
- **Learning system**: Improves recommendations based on usage patterns
- **Community knowledge**: Crowdsourced troubleshooting database
- **Multi-language support**: Buggle speaks your language
- **Personality customization**: Adjust Buggle's communication style

### Phase 3: Enterprise Features
- **Bulk deployment**: Install across multiple machines
- **Configuration management**: Centralized settings and policies
- **Audit trails**: Track installations and compliance
- **Custom repositories**: Private package mirrors and extensions

### Phase 4: Developer Ecosystem
- **Plugin system**: Third-party installer extensions
- **Template marketplace**: Pre-configured project setups
- **Integration APIs**: Embed installer in other tools
- **White-label options**: Customize branding and features

## 📚 Developer Guide

### Adding New Environment Support

1. **Update EnvironmentType enum**:
   ```python
   class EnvironmentType(Enum):
       NEW_ENVIRONMENT = "new_environment"
   ```

2. **Implement detection logic**:
   ```python
   def _detect_new_environment(self) -> bool:
       # Check for environment-specific indicators
       return os.path.exists('/path/to/indicator')
   ```

3. **Add dependency management**:
   ```python
   def _install_deps_new_environment(self) -> Tuple[bool, str]:
       # Environment-specific installation logic
       pass
   ```

4. **Create troubleshooting guide**:
   ```python
   def _get_new_environment_troubleshooting(self) -> list[str]:
       return [
           "🔧 **New Environment Detected**",
           "• Step-by-step instructions",
           "• Common issues and solutions"
       ]
   ```

### Testing New Environments

1. **Create test environment**: Docker container, VM, or cloud instance
2. **Run installer**: `python3 install.py --local /path/to/debuggle`
3. **Verify detection**: Check logs for correct environment identification
4. **Test features**: Ensure VS Code integration and server startup work
5. **Document**: Add to environment support matrix

## 🤝 Contributing

The one-click installer system is designed to be community-driven:

1. **Environment Support**: Add detection for new platforms
2. **Troubleshooting**: Improve error messages and recovery
3. **UI/UX**: Enhance the web installer interface
4. **Documentation**: Help users understand their options

See `CONTRIBUTING.md` for detailed guidelines.

---

## 🎉 The Promise

With this installer system, anyone can go from "never heard of Debuggle" to "actively monitoring errors in VS Code" with a single command. No environment too complex, no setup too difficult - it just works.

**One command. Every environment. Zero friction.**