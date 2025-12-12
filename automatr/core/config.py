"""Configuration management for Automatr.

Handles loading/saving app configuration from a single JSON file.
"""

import json
import platform
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


def get_platform() -> str:
    """Get the current platform.
    
    Returns:
        'windows', 'linux', 'wsl2', or 'macos'
    """
    system = platform.system()
    
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    elif system == "Linux":
        # Check for WSL2
        try:
            with open("/proc/version", "r") as f:
                version = f.read().lower()
                if "microsoft" in version or "wsl" in version:
                    return "wsl2"
        except (OSError, IOError):
            pass
        return "linux"
    return "unknown"


def is_windows() -> bool:
    """Check if running on native Windows."""
    return get_platform() == "windows"


def get_config_dir() -> Path:
    """Get the configuration directory path.
    
    On macOS: ~/Library/Application Support/automatr
    On Linux/WSL: XDG_CONFIG_HOME or ~/.config/automatr
    """
    import os

    system = platform.system()
    if system == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            base = Path(xdg_config)
        else:
            base = Path.home() / ".config"
    
    config_dir = base / "automatr"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    """Get the configuration file path."""
    return get_config_dir() / "config.json"


def get_templates_dir() -> Path:
    """Get the templates directory path."""
    templates_dir = get_config_dir() / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    return templates_dir


def get_improvement_prompt_path() -> Path:
    """Get the path to the improvement prompt template file."""
    return get_config_dir() / "improvement_prompt.txt"


# Default improvement prompt template with placeholders
DEFAULT_IMPROVEMENT_PROMPT = """You are a prompt engineering expert. Modify the template below based on user feedback.

User feedback may ask you to:
- ADD new content or sections
- REMOVE existing content or sections
- MODIFY or rewrite existing content
- RESTRUCTURE the template

CURRENT TEMPLATE:
---START TEMPLATE---
{{template_content}}
---END TEMPLATE---

{{refinements}}

{{additional_notes}}

CRITICAL INSTRUCTIONS:
- Output ONLY the modified template text
- If asked to REMOVE something, your output must NOT contain that content
- NEVER duplicate or repeat sections - output the template exactly once
- Do NOT include any explanations, commentary, or meta-text
- Do NOT include markdown code blocks or formatting markers
- Do NOT include phrases like 'Here is the improved template'
- Keep all {{variable_name}} placeholders exactly as they appear in the original
- The output should be ready to use directly as a prompt template

OUTPUT THE MODIFIED TEMPLATE NOW:"""


def load_improvement_prompt() -> str:
    """Load the improvement prompt template from file.
    
    Returns the default if file doesn't exist.
    """
    path = get_improvement_prompt_path()
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            pass
    return DEFAULT_IMPROVEMENT_PROMPT


def save_improvement_prompt(prompt: str) -> bool:
    """Save the improvement prompt template to file.
    
    Args:
        prompt: The prompt template text.
        
    Returns:
        True if saved successfully, False otherwise.
    """
    path = get_improvement_prompt_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(prompt, encoding="utf-8")
        return True
    except OSError:
        return False


def reset_improvement_prompt() -> bool:
    """Reset the improvement prompt to the default.
    
    Returns:
        True if reset successfully, False otherwise.
    """
    return save_improvement_prompt(DEFAULT_IMPROVEMENT_PROMPT)


# --- Generation Prompt System ---

def get_generation_prompt_path() -> Path:
    """Get the path to the generation prompt template file."""
    return get_config_dir() / "generation_prompt.txt"


# Default generation prompt template with placeholders
DEFAULT_GENERATION_PROMPT = """You are a prompt template creator. Generate a reusable prompt template based on the user's description.

USER DESCRIPTION:
{{description}}

REQUIRED VARIABLES (must appear in output as {{variable_name}}):
{{variables}}

INSTRUCTIONS:
- Create a clear, focused prompt template for the described task
- Include ALL required variables using exactly {{variable_name}} syntax
- Place variables in logical, deterministic positions
- Keep the template concise and actionable
- Use a clear role statement at the start (e.g., "You are a...")
- Include numbered output sections if multiple outputs are needed
- Do NOT include any explanations or commentary
- Output ONLY the template text, ready to use

OUTPUT THE TEMPLATE NOW:"""


def load_generation_prompt() -> str:
    """Load the generation prompt template from file.
    
    Returns the default if file doesn't exist.
    """
    path = get_generation_prompt_path()
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            pass
    return DEFAULT_GENERATION_PROMPT


def save_generation_prompt(prompt: str) -> bool:
    """Save the generation prompt template to file.
    
    Args:
        prompt: The prompt template text.
        
    Returns:
        True if saved successfully, False otherwise.
    """
    path = get_generation_prompt_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(prompt, encoding="utf-8")
        return True
    except OSError:
        return False


def reset_generation_prompt() -> bool:
    """Reset the generation prompt to the default.
    
    Returns:
        True if reset successfully, False otherwise.
    """
    return save_generation_prompt(DEFAULT_GENERATION_PROMPT)


@dataclass
class LLMConfig:
    """Configuration for the local LLM server."""
    
    model_path: str = ""
    model_dir: str = ""
    server_port: int = 8080
    context_size: int = 4096
    gpu_layers: int = 0
    server_binary: str = ""  # Auto-detect if empty
    
    # Generation parameters (live-tunable)
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    top_k: int = 40
    repeat_penalty: float = 1.1


@dataclass
class UIConfig:
    """Configuration for the UI."""
    
    theme: str = "dark"
    window_width: int = 900
    window_height: int = 700
    font_size: int = 13  # Base font size for text content
    
    # Window state persistence
    window_x: int = -1  # -1 = center on screen
    window_y: int = -1  # -1 = center on screen
    window_maximized: bool = False
    window_geometry: str = ""  # Base64 encoded QByteArray
    
    # Layout persistence
    splitter_sizes: list = field(default_factory=lambda: [200, 300, 400])
    
    # Selection persistence
    last_template: str = ""
    expanded_folders: list = field(default_factory=list)
    last_editor_folder: str = ""
    
    # Template versioning
    max_template_versions: int = 10  # Max versions to keep per template (original always preserved)


@dataclass
class EspansoConfig:
    """Configuration for Espanso integration."""
    
    enabled: bool = True
    config_path: str = ""  # Auto-detect if empty
    auto_sync: bool = True  # Auto-sync on template save/delete


@dataclass
class Config:
    """Main application configuration."""
    
    llm: LLMConfig = field(default_factory=LLMConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    espanso: EspansoConfig = field(default_factory=EspansoConfig)
    
    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create config from dictionary."""
        llm_data = data.get("llm", {})
        ui_data = data.get("ui", {})
        espanso_data = data.get("espanso", {})
        
        return cls(
            llm=LLMConfig(**llm_data) if llm_data else LLMConfig(),
            ui=UIConfig(**ui_data) if ui_data else UIConfig(),
            espanso=EspansoConfig(**espanso_data) if espanso_data else EspansoConfig(),
        )


class ConfigManager:
    """Manages loading and saving application configuration."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize ConfigManager.
        
        Args:
            config_path: Path to config file. Uses default if None.
        """
        self.config_path = config_path or get_config_path()
        self._config: Optional[Config] = None
    
    @property
    def config(self) -> Config:
        """Get the current configuration, loading if necessary."""
        if self._config is None:
            self._config = self.load()
        return self._config
    
    def load(self) -> Config:
        """Load configuration from file.
        
        Returns:
            Config object (defaults if file doesn't exist).
        """
        if not self.config_path.exists():
            return Config()
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Config.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # Log error and return defaults
            print(f"Warning: Failed to load config: {e}")
            return Config()
    
    def save(self, config: Optional[Config] = None) -> bool:
        """Save configuration to file.
        
        Args:
            config: Config to save. Uses current config if None.
            
        Returns:
            True if saved successfully, False otherwise.
        """
        if config is None:
            config = self.config
        
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config.to_dict(), f, indent=2)
            self._config = config
            return True
        except OSError as e:
            print(f"Error: Failed to save config: {e}")
            return False
    
    def update(self, **kwargs) -> bool:
        """Update specific config values and save.
        
        Supports nested keys like 'llm.model_path'.
        
        Args:
            **kwargs: Key-value pairs to update.
            
        Returns:
            True if saved successfully, False otherwise.
        """
        config = self.config
        
        for key, value in kwargs.items():
            parts = key.split(".")
            if len(parts) == 2:
                section, attr = parts
                if hasattr(config, section):
                    section_obj = getattr(config, section)
                    if hasattr(section_obj, attr):
                        setattr(section_obj, attr, value)
            elif len(parts) == 1:
                if hasattr(config, key):
                    setattr(config, key, value)
        
        return self.save(config)


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global ConfigManager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> Config:
    """Get the current configuration."""
    return get_config_manager().config


def save_config(config: Optional[Config] = None) -> bool:
    """Save the configuration to file.
    
    Args:
        config: Config to save. Uses current config if None.
        
    Returns:
        True if saved successfully, False otherwise.
    """
    return get_config_manager().save(config)
