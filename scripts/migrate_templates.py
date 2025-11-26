#!/usr/bin/env python3
"""Migrate templates from prompt-automation to automatr format.

This script converts templates from the old format (with id, style, etc.)
to the new simplified format used by automatr.

Usage:
    python migrate_templates.py /path/to/old/prompts/styles
"""

import json
import sys
from pathlib import Path


def migrate_template(old_data: dict) -> dict:
    """Convert old template format to new format."""
    # Extract fields
    name = old_data.get("title", "Untitled")
    
    # Build content from template lines
    template_lines = old_data.get("template", [])
    if isinstance(template_lines, list):
        content = "\n".join(template_lines)
    else:
        content = str(template_lines)
    
    # Convert placeholders to variables
    variables = []
    old_placeholders = old_data.get("placeholders", [])
    for p in old_placeholders:
        var = {
            "name": p.get("name", ""),
            "label": p.get("label", p.get("name", "")),
        }
        if p.get("default"):
            var["default"] = p["default"]
        if p.get("multiline"):
            var["multiline"] = True
        variables.append(var)
    
    # Build new template
    new_data = {
        "name": name,
        "content": content,
    }
    
    # Add optional fields
    description = old_data.get("metadata", {}).get("description", "")
    if description:
        new_data["description"] = description
    
    # Try to generate a trigger from the title
    trigger = ":" + name.lower().replace(" ", "_")[:10]
    new_data["trigger"] = trigger
    
    if variables:
        new_data["variables"] = variables
    
    return new_data


def migrate_directory(source_dir: Path, dest_dir: Path):
    """Migrate all templates from source to destination directory."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for old_file in source_dir.glob("*.json"):
        try:
            with open(old_file, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            
            new_data = migrate_template(old_data)
            
            # Generate safe filename
            safe_name = new_data["name"].lower().replace(" ", "_")
            safe_name = "".join(c for c in safe_name if c.isalnum() or c == "_")
            new_file = dest_dir / f"{safe_name}.json"
            
            with open(new_file, "w", encoding="utf-8") as f:
                json.dump(new_data, f, indent=2)
            
            print(f"Migrated: {old_file.name} -> {new_file.name}")
            count += 1
            
        except Exception as e:
            print(f"Error migrating {old_file}: {e}")
    
    print(f"\nMigrated {count} templates to {dest_dir}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python migrate_templates.py /path/to/old/prompts/styles")
        print("\nThis will migrate templates to ~/.config/automatr/templates/")
        sys.exit(1)
    
    source = Path(sys.argv[1])
    if not source.exists():
        print(f"Error: Source directory not found: {source}")
        sys.exit(1)
    
    # Determine destination
    import os
    config_home = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    dest = Path(config_home) / "automatr" / "templates"
    
    print(f"Migrating templates from: {source}")
    print(f"Migrating templates to:   {dest}")
    print()
    
    migrate_directory(source, dest)


if __name__ == "__main__":
    main()
