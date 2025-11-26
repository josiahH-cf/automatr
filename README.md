# Automatr

Minimal prompt automation tool with local LLM integration.

## Features

- **Template-driven prompts** — JSON-based templates with variables
- **Local LLM** — Integrates with llama.cpp server
- **Espanso triggers** — Map templates to text expansion triggers
- **Global hotkey** — AutoHotkey script for Windows/WSL2
- **PyQt6 GUI** — Clean, dark-themed interface

## Quick Start

```bash
# Install
./install.sh

# Run
automatr
```

## Usage

```bash
# Launch GUI
automatr

# Sync templates to Espanso
automatr --sync

# Show version
automatr --version
```

## Configuration

Configuration is stored in `~/.config/automatr/config.json`:

```json
{
  "model_path": "~/models/llama-3.2-3b.gguf",
  "server_port": 8080,
  "theme": "dark"
}
```

## Templates

Templates are stored in `~/.config/automatr/templates/`:

```json
{
  "name": "Code Review",
  "description": "Ask an LLM to review code",
  "trigger": ":review",
  "variables": [
    { "name": "language", "label": "Language", "default": "Python" },
    { "name": "code", "label": "Code", "multiline": true }
  ],
  "content": "Review this {{language}} code:\n\n{{code}}"
}
```

## License

MIT
