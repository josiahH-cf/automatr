#!/usr/bin/env bash
#
# Automatr Unified Installer
#
# This script installs Automatr and all its dependencies on:
# - Ubuntu/Debian Linux
# - WSL2 (Windows Subsystem for Linux)
# - macOS (experimental)
#
# Usage:
#   ./install.sh          # Interactive installation
#   ./install.sh --quick  # Quick install with defaults
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"

# Platform-specific paths (set after detect_platform)
DATA_DIR=""
CONFIG_DIR=""
LLAMA_CPP_DIR=""

set_platform_paths() {
    if [[ "$PLATFORM" == "macos" ]]; then
        DATA_DIR="$HOME/Library/Application Support/automatr"
        CONFIG_DIR="$DATA_DIR"
    else
        DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/automatr"
        CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/automatr"
    fi
    LLAMA_CPP_DIR="${DATA_DIR}/llama.cpp"
}

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect platform
detect_platform() {
    OS="$(uname -s)"
    ARCH="$(uname -m)"
    IS_WSL2=false
    
    # Check for native Windows (Git Bash, MSYS2, etc.)
    if [[ "$OS" == MINGW* ]] || [[ "$OS" == MSYS* ]] || [[ "$OS" == CYGWIN* ]]; then
        echo ""
        log_warn "Native Windows detected!"
        echo ""
        echo "  This bash installer is for Linux/WSL2/macOS."
        echo "  For Windows, run the PowerShell installer instead:"
        echo ""
        echo -e "    ${BLUE}powershell -ExecutionPolicy Bypass -File scripts/install_ahk.ps1${NC}"
        echo ""
        echo "  This will install AutoHotkey for global hotkey support."
        echo "  Hotkey: Ctrl+Shift+J (configurable in Settings menu)"
        echo ""
        exit 0
    fi
    
    if [[ -f /proc/version ]] && grep -qi "microsoft\|wsl" /proc/version 2>/dev/null; then
        IS_WSL2=true
    fi
    
    case "$OS" in
        Linux*)
            if $IS_WSL2; then
                PLATFORM="wsl2"
            else
                PLATFORM="linux"
            fi
            ;;
        Darwin*)
            PLATFORM="macos"
            ;;
        *)
            log_error "Unsupported operating system: $OS"
            exit 1
            ;;
    esac
    
    log_info "Detected platform: $PLATFORM ($ARCH)"
}

# Install system dependencies
install_system_deps() {
    log_info "Installing system dependencies..."
    
    case "$PLATFORM" in
        linux|wsl2)
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y \
                    python3 python3-pip python3-venv \
                    build-essential cmake git \
                    libgl1-mesa-dev libxcb-xinerama0 \
                    qt6-base-dev libqt6widgets6 \
                    2>/dev/null || {
                        # Fallback for older Ubuntu
                        sudo apt-get install -y \
                            python3 python3-pip python3-venv \
                            build-essential cmake git \
                            libgl1-mesa-glx
                    }
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y \
                    python3 python3-pip \
                    gcc-c++ cmake git \
                    qt6-qtbase-devel
            else
                log_warn "Package manager not recognized. Please install manually:"
                log_warn "  - Python 3.10+"
                log_warn "  - build-essential/gcc, cmake, git"
                log_warn "  - Qt6 base libraries"
            fi
            ;;
        macos)
            if ! command -v brew &> /dev/null; then
                log_error "Homebrew is required. Install it from https://brew.sh"
                exit 1
            fi
            # Ensure Xcode Command Line Tools are installed
            if ! xcode-select -p &> /dev/null; then
                log_info "Installing Xcode Command Line Tools..."
                xcode-select --install
                log_warn "Please wait for Xcode CLI tools to finish installing, then re-run this script."
                exit 0
            fi
            brew install python@3.11 cmake qt@6 git
            ;;
    esac
    
    log_success "System dependencies installed"
}

# Create Python virtual environment
setup_python_env() {
    log_info "Setting up Python virtual environment..."
    
    if [[ ! -d "$VENV_DIR" ]]; then
        python3 -m venv "$VENV_DIR"
    fi
    
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip wheel setuptools
    
    # Install automatr
    pip install -e "$SCRIPT_DIR"
    
    log_success "Python environment ready: $VENV_DIR"
}

# Build llama.cpp from source
build_llama_cpp() {
    log_info "Setting up llama.cpp..."
    
    if [[ -f "$LLAMA_CPP_DIR/build/bin/llama-server" ]]; then
        log_success "llama-server already built"
        return
    fi
    
    # Ensure data directory exists
    mkdir -p "$DATA_DIR"
    
    # Clone if not present
    if [[ ! -d "$LLAMA_CPP_DIR" ]]; then
        log_info "Cloning llama.cpp to $LLAMA_CPP_DIR..."
        git clone --depth 1 https://github.com/ggerganov/llama.cpp.git "$LLAMA_CPP_DIR"
    fi
    
    cd "$LLAMA_CPP_DIR"
    
    # Build
    log_info "Building llama.cpp (this may take a few minutes)..."
    
    mkdir -p build
    cd build
    
    # Detect GPU support
    CMAKE_ARGS=""
    if command -v nvcc &> /dev/null; then
        log_info "CUDA detected, building with GPU support..."
        CMAKE_ARGS="-DGGML_CUDA=ON"
    elif [[ "$PLATFORM" == "macos" ]]; then
        log_info "Building with Metal support..."
        CMAKE_ARGS="-DGGML_METAL=ON"
    fi
    
    cmake .. $CMAKE_ARGS -DCMAKE_BUILD_TYPE=Release
    cmake --build . --config Release -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
    
    log_success "llama.cpp built successfully"
    cd "$SCRIPT_DIR"
}

# Setup configuration
setup_config() {
    log_info "Setting up configuration..."
    
    mkdir -p "$CONFIG_DIR/templates"
    mkdir -p "$DATA_DIR"
    
    # Copy example templates while respecting existing user placement (folders)
    if [[ -d "$SCRIPT_DIR/templates" ]]; then
        python3 - <<PY
from pathlib import Path
import shutil

src = Path(r"""$SCRIPT_DIR/templates""")
dst = Path(r"""$CONFIG_DIR/templates""")
dst.mkdir(parents=True, exist_ok=True)

# Copy all templates from repo, overwriting any existing files with same name
# This ensures clean baseline templates are always used
for src_file in src.rglob("*.json"):
    target = dst / src_file.relative_to(src)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, target)

print("Synced templates from repository (overwrites enabled)")
PY
    fi
    
    # Create default config if it doesn't exist
    if [[ ! -f "$CONFIG_DIR/config.json" ]]; then
        cat > "$CONFIG_DIR/config.json" << EOF
{
  "llm": {
    "model_path": "",
    "model_dir": "$HOME/models",
    "server_port": 8080,
    "context_size": 4096,
    "gpu_layers": 0,
    "server_binary": ""
  },
  "ui": {
    "theme": "dark",
    "window_width": 900,
    "window_height": 700,
    "font_size": 11
  },
  "espanso": {
    "enabled": true,
    "config_path": "",
    "auto_sync": false
  }
}
EOF
        log_info "Created default configuration"
    fi
    
    log_success "Configuration ready: $CONFIG_DIR"
}

# Setup Espanso integration
setup_espanso() {
    log_info "Setting up Espanso integration..."
    
    # Detect Espanso config directory
    ESPANSO_CONFIG=""
    
    if $IS_WSL2; then
        # Try to find Windows username
        WIN_USER=$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r\n' || echo "")
        if [[ -n "$WIN_USER" ]]; then
            # Prefer Espanso v2 default on Windows
            ESPANSO_CONFIG="/mnt/c/Users/$WIN_USER/.config/espanso"
            if [[ ! -d "$ESPANSO_CONFIG" ]]; then
                ESPANSO_CONFIG="/mnt/c/Users/$WIN_USER/.espanso"
            fi
            if [[ ! -d "$ESPANSO_CONFIG" ]]; then
                ESPANSO_CONFIG="/mnt/c/Users/$WIN_USER/AppData/Roaming/espanso"
            fi
        fi
    else
        if [[ -d "$HOME/.config/espanso" ]]; then
            ESPANSO_CONFIG="$HOME/.config/espanso"
        elif [[ -d "$HOME/.espanso" ]]; then
            ESPANSO_CONFIG="$HOME/.espanso"
        fi
    fi
    
    if [[ -d "$ESPANSO_CONFIG" ]]; then
        log_success "Found Espanso config: $ESPANSO_CONFIG"

        # Persist detected path into automatr config if not already set
        if [[ -f "$CONFIG_DIR/config.json" ]]; then
            python3 - <<PY
import json
from pathlib import Path

config_path = Path(r"""$CONFIG_DIR/config.json""")
data = json.loads(config_path.read_text()) if config_path.exists() else {}
esp = data.get("espanso", {})

if not esp.get("config_path"):
    esp["config_path"] = r"""$ESPANSO_CONFIG"""
    data["espanso"] = esp
    config_path.write_text(json.dumps(data, indent=2))
    print(f"Set espanso.config_path to {esp['config_path']}")
PY
        fi
        
        # Sync templates
        source "$VENV_DIR/bin/activate"
        if automatr --sync; then
            if $IS_WSL2; then
                # WSL2 writes don't trigger Windows file watcher; restart Espanso
                log_info "Restarting Espanso to load triggers..."
                powershell.exe -NoProfile -Command "cd C:/; espanso service stop" &>/dev/null
                if powershell.exe -NoProfile -Command "cd C:/; Start-Process espanso -ArgumentList 'service','start' -WindowStyle Hidden" &>/dev/null; then
                    sleep 1
                    log_success "Espanso restarted successfully"
                else
                    log_warn "Could not restart Espanso. Run 'espanso restart' from Windows PowerShell"
                fi
            fi
        else
            log_warn "Failed to sync templates to Espanso"
        fi
    else
        log_warn "Espanso config not found. Run 'automatr --sync' after installing Espanso."
    fi
}

# Setup AutoHotkey (WSL2 only)
setup_ahk() {
    if ! $IS_WSL2; then
        return
    fi
    
    log_info "Setting up AutoHotkey script..."
    
    # Try to find Windows username
    WIN_USER=$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r\n' || echo "")
    
    if [[ -z "$WIN_USER" ]]; then
        log_warn "Could not detect Windows username for AHK setup"
        return
    fi
    
    # Detect current WSL distro name
    WSL_DISTRO=$(wsl.exe -l -q 2>/dev/null | tr -d '\0\r' | grep -v "^$" | grep -vi docker | head -1 || echo "")
    if [[ -z "$WSL_DISTRO" ]]; then
        # Fallback: try to get from /etc/os-release
        WSL_DISTRO=$(grep "^ID=" /etc/os-release 2>/dev/null | cut -d= -f2 | tr -d '"' || echo "Ubuntu")
        # Capitalize first letter
        WSL_DISTRO="$(echo "${WSL_DISTRO:0:1}" | tr '[:lower:]' '[:upper:]')${WSL_DISTRO:1}"
    fi
    log_info "Detected WSL distro: $WSL_DISTRO"
    
    # Generate AHK script with correct paths
    AHK_DEST="/mnt/c/Users/$WIN_USER/Documents/AutoHotkey/automatr.ahk"
    mkdir -p "$(dirname "$AHK_DEST")"
    
    cat > "$AHK_DEST" << EOF
; Automatr - Press Ctrl+Shift+J to launch
; Auto-generated by install.sh
#SingleInstance Force

^+j::
    IfWinExist, Automatr
        WinActivate
    else
        Run, wsl.exe -d $WSL_DISTRO bash -c "QT_QPA_PLATFORM=xcb $VENV_DIR/bin/automatr", , Hide
return
EOF
    
    if [[ ! -f "$AHK_DEST" ]]; then
        log_warn "Could not create AutoHotkey script"
        return
    fi
    
    log_success "AutoHotkey script created: $AHK_DEST"
    
    # Copy to Windows Startup folder
    STARTUP_DIR="/mnt/c/Users/$WIN_USER/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
    if [[ -d "$STARTUP_DIR" ]]; then
        cp "$AHK_DEST" "$STARTUP_DIR/automatr.ahk" 2>/dev/null && \
            log_success "Added to Windows Startup - Ctrl+Shift+J will work after restart" || \
            log_warn "Could not add to Windows Startup"
    fi
    
    # Check if AutoHotkey is installed
    AHK_INSTALLED=false
    if [[ -f "/mnt/c/Program Files/AutoHotkey/AutoHotkey.exe" ]]; then
        log_success "AutoHotkey detected"
        AHK_INSTALLED=true
    else
        log_warn "AutoHotkey not found"
        log_info "Install AutoHotkey v1.1 from: https://www.autohotkey.com/download/ahk-install.exe"
    fi
}

# Create shell alias
setup_alias() {
    log_info "Setting up shell alias..."
    
    SHELL_RC=""
    if [[ -f "$HOME/.zshrc" ]]; then
        SHELL_RC="$HOME/.zshrc"
    elif [[ -f "$HOME/.bashrc" ]]; then
        SHELL_RC="$HOME/.bashrc"
    fi
    
    if [[ -n "$SHELL_RC" ]]; then
        ALIAS_LINE="alias automatr='source $VENV_DIR/bin/activate && automatr'"
        
        if ! grep -q "alias automatr=" "$SHELL_RC" 2>/dev/null; then
            echo "" >> "$SHELL_RC"
            echo "# Automatr" >> "$SHELL_RC"
            echo "$ALIAS_LINE" >> "$SHELL_RC"
            log_success "Added alias to $SHELL_RC"
        fi
    fi
}

# Run smoke test
smoke_test() {
    log_info "Running smoke test..."
    
    source "$VENV_DIR/bin/activate"
    
    # Test import
    if python3 -c "import automatr; print(f'Version: {automatr.__version__}')" 2>/dev/null; then
        log_success "Import test passed"
    else
        log_error "Import test failed"
        return 1
    fi
    
    # Test config
    if python3 -c "from automatr.core.config import get_config; get_config()" 2>/dev/null; then
        log_success "Config test passed"
    else
        log_error "Config test failed"
        return 1
    fi
    
    # Test templates
    if python3 -c "from automatr.core.templates import get_template_manager; print(f'Templates: {len(get_template_manager().list_all())}')" 2>/dev/null; then
        log_success "Template test passed"
    else
        log_error "Template test failed"
        return 1
    fi
    
    # Check llama-server
    if [[ -f "$LLAMA_CPP_DIR/build/bin/llama-server" ]]; then
        log_success "llama-server binary found"
    else
        log_warn "llama-server not found - LLM features will be unavailable"
    fi
    
    log_success "Smoke test complete!"
}

# Print summary
print_summary() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                  Automatr Installation Complete             ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BLUE}Virtual environment:${NC} $VENV_DIR"
    echo -e "  ${BLUE}Configuration:${NC}       $CONFIG_DIR"
    echo -e "  ${BLUE}Data directory:${NC}      $DATA_DIR"
    echo -e "  ${BLUE}llama.cpp:${NC}           $LLAMA_CPP_DIR"
    echo ""
    echo -e "  ${YELLOW}To start Automatr:${NC}"
    echo -e "    source $VENV_DIR/bin/activate"
    echo -e "    automatr"
    echo ""
    echo -e "  ${YELLOW}Or restart your shell and run:${NC}"
    echo -e "    automatr"
    echo ""
    if $IS_WSL2; then
        echo -e "  ${YELLOW}Windows global hotkey (Ctrl+Shift+J):${NC}"
        if [[ -f "/mnt/c/Program Files/AutoHotkey/AutoHotkey.exe" ]]; then
            echo -e "    ${GREEN}✓${NC} AutoHotkey installed"
            echo -e "    Runs automatically on Windows startup"
            echo -e "    Or double-click: Documents/AutoHotkey/automatr.ahk"
        else
            echo -e "    ${RED}✗${NC} AutoHotkey not installed"
            echo -e "    Install from: https://www.autohotkey.com/download/ahk-install.exe"
            echo -e "    Then double-click: Documents/AutoHotkey/automatr.ahk"
        fi
        echo ""
    fi
    echo -e "  ${YELLOW}Next steps:${NC}"
    echo -e "    1. Download a GGUF model to ~/models/"
    echo -e "    2. Select model in LLM menu or edit $CONFIG_DIR/config.json"
    echo -e "    3. Run 'automatr' to start the GUI"
    echo ""
}

# Main installation
main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                    Automatr Installer                       ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    detect_platform
    set_platform_paths
    
    if [[ "$1" != "--quick" ]]; then
        echo ""
        log_info "This will install:"
        echo "  - System dependencies (Python, Qt6, cmake, etc.)"
        echo "  - Python virtual environment with PyQt6"
        echo "  - llama.cpp (built from source)"
        echo "  - Example templates"
        echo ""
        read -p "Continue? [Y/n] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            log_info "Installation cancelled"
            exit 0
        fi
    fi
    
    install_system_deps
    setup_python_env
    build_llama_cpp
    setup_config
    setup_espanso
    setup_ahk
    setup_alias
    smoke_test
    print_summary
}

# Run main
main "$@"
