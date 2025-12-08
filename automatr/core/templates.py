"""Template management for Automatr.

Handles loading, saving, and rendering JSON templates.
Templates are stored as individual JSON files in the templates directory.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Iterator

from automatr.core.config import get_templates_dir


@dataclass
class Variable:
    """A variable/placeholder in a template.
    
    Attributes:
        name: Variable identifier used in content placeholders.
        label: Display label for UI/forms.
        default: Default value.
        multiline: Whether to use multiline input (form type only).
        type: Variable type - "form" (default), "date", etc.
        params: Type-specific parameters (e.g., {"format": "%Y-%m-%d"} for date).
    """
    
    name: str
    label: str = ""
    default: str = ""
    multiline: bool = False
    type: str = "form"  # "form", "date"
    params: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.label:
            self.label = self.name.replace("_", " ").title()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = {"name": self.name, "label": self.label}
        if self.default:
            d["default"] = self.default
        if self.multiline:
            d["multiline"] = True
        if self.type != "form":
            d["type"] = self.type
        if self.params:
            d["params"] = self.params
        return d
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Variable":
        """Create from dictionary."""
        label = data.get("label", "")
        if label is None or isinstance(label, (dict, list)):
            label = str(label) if label not in (None, {}) else ""
        elif not isinstance(label, str):
            label = str(label)
        default = data.get("default", "")
        if default is None or isinstance(default, (dict, list)):  # keep UI inputs from crashing
            default = str(default) if default not in (None, {}) else ""
        elif not isinstance(default, str):
            default = str(default)
        return cls(
            name=data.get("name", ""),
            label=label,
            default=default,
            multiline=data.get("multiline", False),
            type=data.get("type", "form"),
            params=data.get("params", {}),
        )


@dataclass
class Template:
    """A prompt template."""
    
    name: str
    content: str
    description: str = ""
    trigger: str = ""  # Espanso trigger (e.g., ":review")
    variables: List[Variable] = field(default_factory=list)
    
    # Internal: path to the JSON file (set when loaded from disk)
    _path: Optional[Path] = field(default=None, repr=False)
    
    @property
    def filename(self) -> str:
        """Generate a safe filename from the template name."""
        # Convert to lowercase, replace spaces with underscores
        safe = self.name.lower().replace(" ", "_")
        # Remove non-alphanumeric characters except underscores
        safe = re.sub(r"[^a-z0-9_]", "", safe)
        return f"{safe}.json"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        d = {
            "name": self.name,
            "content": self.content,
        }
        if self.description:
            d["description"] = self.description
        if self.trigger:
            d["trigger"] = self.trigger
        if self.variables:
            d["variables"] = [v.to_dict() for v in self.variables]
        return d
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], path: Optional[Path] = None) -> "Template":
        """Create from dictionary."""
        variables = [
            Variable.from_dict(v) for v in data.get("variables", [])
        ]
        return cls(
            name=data.get("name", "Untitled"),
            content=data.get("content", ""),
            description=data.get("description", ""),
            trigger=data.get("trigger", ""),
            variables=variables,
            _path=path,
        )
    
    def render(self, values: Dict[str, str]) -> str:
        """Render the template with the given variable values.
        
        Replaces {{variable_name}} placeholders with their values.
        
        Args:
            values: Dictionary of variable name -> value.
            
        Returns:
            Rendered template string.
        """
        result = self.content
        
        for var in self.variables:
            placeholder = f"{{{{{var.name}}}}}"
            value = values.get(var.name, var.default)
            result = result.replace(placeholder, value)
        
        # Remove any unreplaced placeholders
        result = re.sub(r"\{\{[^}]+\}\}", "", result)
        
        return result


class TemplateManager:
    """Manages template CRUD operations.
    
    Templates are stored as individual JSON files in the templates directory.
    No SQLite, no indexing — just filesystem operations.
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize TemplateManager.
        
        Args:
            templates_dir: Directory for template files. Uses default if None.
        """
        self.templates_dir = templates_dir or get_templates_dir()
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def list_all(self) -> List[Template]:
        """List all templates.
        
        Returns:
            List of Template objects, sorted by name.
        """
        templates = []
        for path in self.templates_dir.glob("**/*.json"):
            try:
                template = self.load(path)
                if template:
                    templates.append(template)
            except Exception as e:
                print(f"Warning: Failed to load {path}: {e}")
        
        return sorted(templates, key=lambda t: t.name.lower())
    
    def load(self, path: Path) -> Optional[Template]:
        """Load a template from a JSON file.
        
        Args:
            path: Path to the JSON file.
            
        Returns:
            Template object, or None if loading failed.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Template.from_dict(data, path=path)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error loading template {path}: {e}")
            return None
    
    def get(self, name: str) -> Optional[Template]:
        """Get a template by name.
        
        Args:
            name: Template name.
            
        Returns:
            Template object, or None if not found.
        """
        # Create expected filename
        safe_name = name.lower().replace(" ", "_")
        safe_name = re.sub(r"[^a-z0-9_]", "", safe_name)
        path = self.templates_dir / f"{safe_name}.json"
        
        if path.exists():
            return self.load(path)
        
        # Fallback: search all templates
        for template in self.list_all():
            if template.name.lower() == name.lower():
                return template
        
        return None
    
    def save(self, template: Template) -> bool:
        """Save a template to disk.
        
        Args:
            template: Template to save.
            
        Returns:
            True if saved successfully, False otherwise.
        """
        # Determine path
        if template._path:
            path = template._path
        else:
            path = self.templates_dir / template.filename
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(template.to_dict(), f, indent=2)
            template._path = path
            return True
        except OSError as e:
            print(f"Error saving template: {e}")
            return False
    
    def delete(self, template: Template) -> bool:
        """Delete a template from disk.
        
        Args:
            template: Template to delete.
            
        Returns:
            True if deleted successfully, False otherwise.
        """
        if not template._path or not template._path.exists():
            return False
        
        try:
            template._path.unlink()
            return True
        except OSError as e:
            print(f"Error deleting template: {e}")
            return False
    
    def create(
        self,
        name: str,
        content: str,
        description: str = "",
        trigger: str = "",
        variables: Optional[List[Dict[str, Any]]] = None,
    ) -> Template:
        """Create and save a new template.
        
        Args:
            name: Template name.
            content: Template content with {{variable}} placeholders.
            description: Optional description.
            trigger: Optional Espanso trigger.
            variables: Optional list of variable dicts.
            
        Returns:
            The created Template object.
        """
        var_list = []
        if variables:
            var_list = [Variable.from_dict(v) for v in variables]
        
        template = Template(
            name=name,
            content=content,
            description=description,
            trigger=trigger,
            variables=var_list,
        )
        
        self.save(template)
        return template
    
    def iter_with_triggers(self) -> Iterator[Template]:
        """Iterate over templates that have Espanso triggers.
        
        Yields:
            Templates with non-empty trigger field.
        """
        for template in self.list_all():
            if template.trigger:
                yield template
    
    def list_folders(self) -> List[str]:
        """List all category folders.
        
        Returns:
            List of folder names (relative to templates_dir), sorted alphabetically.
        """
        folders = []
        for path in self.templates_dir.iterdir():
            if path.is_dir():
                folders.append(path.name)
        return sorted(folders, key=str.lower)
    
    def create_folder(self, name: str) -> bool:
        """Create a new category folder.
        
        Args:
            name: Folder name.
            
        Returns:
            True if created successfully, False otherwise.
        """
        # Sanitize folder name
        safe_name = re.sub(r"[^a-zA-Z0-9_ -]", "", name).strip()
        if not safe_name:
            return False
        
        folder_path = self.templates_dir / safe_name
        if folder_path.exists():
            return False
        
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            return True
        except OSError:
            return False
    
    def delete_folder(self, name: str) -> tuple[bool, str]:
        """Delete a category folder (must be empty).
        
        Args:
            name: Folder name.
            
        Returns:
            Tuple of (success, error_message).
        """
        folder_path = self.templates_dir / name
        if not folder_path.exists() or not folder_path.is_dir():
            return False, "Folder does not exist."
        
        # Check if folder has templates
        templates_in_folder = list(folder_path.glob("*.json"))
        if templates_in_folder:
            return False, f"Cannot delete folder '{name}' because it contains {len(templates_in_folder)} template(s). Move or delete them first."
        
        try:
            folder_path.rmdir()
            return True, ""
        except OSError as e:
            return False, str(e)
    
    def get_template_folder(self, template: Template) -> str:
        """Get the folder name for a template.
        
        Args:
            template: Template to check.
            
        Returns:
            Folder name, or empty string if in root.
        """
        if not template._path:
            return ""
        
        parent = template._path.parent
        if parent == self.templates_dir:
            return ""
        return parent.name
    
    def save_to_folder(self, template: Template, folder: str = "") -> bool:
        """Save a template to a specific folder.
        
        Args:
            template: Template to save.
            folder: Folder name (empty string for root).
            
        Returns:
            True if saved successfully, False otherwise.
        """
        # Determine target directory
        if folder:
            target_dir = self.templates_dir / folder
            target_dir.mkdir(parents=True, exist_ok=True)
        else:
            target_dir = self.templates_dir
        
        # If template already has a path in a different location, we're moving it
        old_path = template._path
        new_path = target_dir / template.filename
        
        try:
            with open(new_path, "w", encoding="utf-8") as f:
                json.dump(template.to_dict(), f, indent=2)
            
            # Remove old file if we moved it
            if old_path and old_path != new_path and old_path.exists():
                old_path.unlink()
            
            template._path = new_path
            return True
        except OSError as e:
            print(f"Error saving template: {e}")
            return False


# Global template manager instance
_template_manager: Optional[TemplateManager] = None


def get_template_manager() -> TemplateManager:
    """Get the global TemplateManager instance."""
    global _template_manager
    if _template_manager is None:
        _template_manager = TemplateManager()
    return _template_manager
