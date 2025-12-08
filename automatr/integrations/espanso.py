"""Espanso integration for Automatr.

Generates Espanso match files from templates that have triggers defined.
"""

import platform
from pathlib import Path
from typing import Optional

import yaml

from automatr.core.config import get_config
from automatr.core.templates import get_template_manager


def _convert_to_espanso_placeholders(content: str, variables) -> str:
    """Convert template placeholders {{var}} to Espanso placeholders.
    
    Form variables use {{var.value}} for accessing the value.
    Date and other simple types use {{var}} directly.
    """
    updated = content
    for var in variables:
        name = var.name
        var_type = getattr(var, 'type', 'form')
        
        if var_type == "form":
            # Form variables with layout return objects; access via .value
            updated = updated.replace(f"{{{{{name}}}}}", f"{{{{{name}.value}}}}")
            updated = updated.replace(f"{{{{ {name} }}}}", f"{{{{{name}.value}}}}")
        # Date and other simple types use {{var}} directly (no conversion needed)
    return updated


def _build_espanso_var_entry(var) -> dict:
    """Build an Espanso variable entry from a Variable object."""
    var_type = getattr(var, 'type', 'form')
    params = getattr(var, 'params', {})
    
    if var_type == "date":
        var_entry = {
            "name": var.name,
            "type": "date",
        }
        if params:
            var_entry["params"] = params
        return var_entry
    
    # Default: form type
    var_entry = {
        "name": var.name,
        "type": "form",
        "params": {
            # Espanso v2 forms require [[value]] placeholder
            "layout": f"{var.label}: [[value]]",
        },
    }
    if var.default:
        var_entry["params"]["default"] = var.default
    return var_entry


def get_espanso_config_dir() -> Optional[Path]:
    """Get the Espanso configuration directory.
    
    Returns:
        Path to Espanso config directory, or None if not found.
    """
    config = get_config()
    
    # Use configured path if set
    if config.espanso.config_path:
        path = Path(config.espanso.config_path).expanduser()
        if path.exists():
            return path
    
    # Auto-detect based on platform
    system = platform.system()
    
    # Check if running in WSL2
    is_wsl2 = False
    if system == "Linux":
        try:
            with open("/proc/version", "r") as f:
                version = f.read().lower()
                is_wsl2 = "microsoft" in version or "wsl" in version
        except Exception:
            pass
    
    if is_wsl2:
        # Try to find Windows user and use Windows Espanso path
        try:
            import subprocess
            result = subprocess.run(
                ["cmd.exe", "/c", "echo %USERNAME%"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            win_user = result.stdout.strip()
            if win_user:
                # Prefer Espanso v2 default on Windows
                config_path = Path(f"/mnt/c/Users/{win_user}/.config/espanso")
                if config_path.exists():
                    return config_path

                legacy_path = Path(f"/mnt/c/Users/{win_user}/.espanso")
                if legacy_path.exists():
                    return legacy_path

                appdata_path = Path(f"/mnt/c/Users/{win_user}/AppData/Roaming/espanso")
                if appdata_path.exists():
                    return appdata_path
        except Exception:
            pass
    
    # Standard paths
    candidates = []
    
    if system == "Linux":
        candidates = [
            Path.home() / ".config" / "espanso",
            Path.home() / ".espanso",
        ]
    elif system == "Darwin":  # macOS
        candidates = [
            Path.home() / "Library" / "Application Support" / "espanso",
            Path.home() / ".config" / "espanso",
        ]
    elif system == "Windows":
        import os
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            candidates.append(Path(appdata) / "espanso")
        candidates.append(Path.home() / ".espanso")
    
    for path in candidates:
        if path.exists():
            return path
    
    return None


def get_match_dir() -> Optional[Path]:
    """Get the Espanso match directory.
    
    Returns:
        Path to match directory, or None if not found.
    """
    config_dir = get_espanso_config_dir()
    if not config_dir:
        return None
    
    match_dir = config_dir / "match"
    match_dir.mkdir(parents=True, exist_ok=True)
    return match_dir


def sync_to_espanso() -> bool:
    """Sync templates to Espanso match file.
    
    Generates a single `automatr.yml` file containing all templates
    that have triggers defined.
    
    Returns:
        True if sync was successful, False otherwise.
    """
    match_dir = get_match_dir()
    if not match_dir:
        print("Error: Could not find Espanso config directory")
        return False
    
    template_manager = get_template_manager()
    matches = []
    
    for template in template_manager.iter_with_triggers():
        # Build Espanso match entry; use Espanso form placeholders in replacement
        replace_text = _convert_to_espanso_placeholders(template.content, template.variables or [])
        match_entry = {
            "trigger": template.trigger,
            "replace": replace_text,
        }
        
        # Add variables if present
        if template.variables:
            match_entry["vars"] = []
            for var in template.variables:
                var_entry = _build_espanso_var_entry(var)
                match_entry["vars"].append(var_entry)
        
        matches.append(match_entry)
    
    if not matches:
        print("No templates with triggers found")
        return True
    
    # Write YAML file
    output_path = match_dir / "automatr.yml"
    try:
        content = {"matches": matches}
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(content, f, default_flow_style=False, allow_unicode=True)
        
        print(f"Synced {len(matches)} triggers to {output_path}")
        
        # Check if running in WSL2 - file watcher may not detect changes
        is_wsl2 = False
        if platform.system() == "Linux":
            try:
                with open("/proc/version", "r") as f:
                    version = f.read().lower()
                    is_wsl2 = "microsoft" in version or "wsl" in version
            except Exception:
                pass
        
        if is_wsl2:
            # WSL2 file writes don't trigger Windows file watcher; restart Espanso
            try:
                import subprocess
                # Stop espanso first
                subprocess.run(
                    ["powershell.exe", "-NoProfile", "-Command", "cd C:/; espanso service stop"],
                    capture_output=True,
                    timeout=10,
                )
                # Start as detached process (avoids WSL console issues)
                result = subprocess.run(
                    ["powershell.exe", "-NoProfile", "-Command", 
                     "cd C:/; Start-Process espanso -ArgumentList 'service','start' -WindowStyle Hidden"],
                    capture_output=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    print("Espanso restarted successfully.")
                else:
                    print("Note: Run 'espanso restart' from Windows PowerShell to reload triggers.")
            except Exception:
                print("Note: Run 'espanso restart' from Windows PowerShell to reload triggers.")
        
        return True
    except Exception as e:
        print(f"Error writing Espanso file: {e}")
        return False


def restart_espanso() -> bool:
    """Restart the Espanso daemon.
    
    Returns:
        True if restart was successful, False otherwise.
    """
    import subprocess
    import shutil
    
    # Check if running in WSL2
    is_wsl2 = False
    if platform.system() == "Linux":
        try:
            with open("/proc/version", "r") as f:
                version = f.read().lower()
                is_wsl2 = "microsoft" in version or "wsl" in version
        except Exception:
            pass
    
    if is_wsl2:
        # Restart Windows Espanso via PowerShell
        try:
            subprocess.run(
                ["powershell.exe", "-Command", "espanso restart"],
                capture_output=True,
                timeout=10,
            )
            return True
        except Exception:
            pass
    
    # Try native espanso command
    if shutil.which("espanso"):
        try:
            subprocess.run(["espanso", "restart"], capture_output=True, timeout=10)
            return True
        except Exception:
            pass
    
    return False


class EspansoManager:
    """Manager for Espanso integration."""
    
    def __init__(self):
        self.config_dir = get_espanso_config_dir()
        self.match_dir = get_match_dir()
    
    def is_available(self) -> bool:
        """Check if Espanso is available."""
        return self.match_dir is not None
    
    def sync(self) -> int:
        """Sync templates to Espanso and return count of synced templates."""
        if not self.match_dir:
            return 0
        
        template_manager = get_template_manager()
        matches = []
        
        for template in template_manager.iter_with_triggers():
            replace_text = _convert_to_espanso_placeholders(template.content, template.variables or [])
            match_entry = {
                "trigger": template.trigger,
                "replace": replace_text,
            }
            
            if template.variables:
                match_entry["vars"] = []
                for var in template.variables:
                    var_entry = _build_espanso_var_entry(var)
                    match_entry["vars"].append(var_entry)
            
            matches.append(match_entry)
        
        if not matches:
            return 0
        
        # Write YAML file
        output_path = self.match_dir / "automatr.yml"
        try:
            content = {"matches": matches}
            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(content, f, default_flow_style=False, allow_unicode=True)
            return len(matches)
        except Exception:
            return 0
    
    def restart(self) -> bool:
        """Restart Espanso daemon."""
        return restart_espanso()


# Global instance
_espanso_manager: Optional[EspansoManager] = None


def get_espanso_manager() -> EspansoManager:
    """Get the global Espanso manager."""
    global _espanso_manager
    if _espanso_manager is None:
        _espanso_manager = EspansoManager()
    return _espanso_manager
