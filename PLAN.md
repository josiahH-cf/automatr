# Automatr: Refactor Plan

This document outlines the comprehensive plan to create **Automatr**, a minimal, stable, and maintainable automation tool built from a clean-room implementation. The original `prompt-automation` repository serves only as a reference; this repository is the target for new, simplified code.

---

## High-Level Goal

Transform the complex original project into a **minimal, stable, and maintainable tool** that does only the following:

1. **Template-driven prompt creation** — JSON-based templates with variables, easy to edit.
2. **Local model integration** — Manage and interact with a `llama.cpp` server.
3. **Text expansion via Espanso** — Map templates to triggers.
4. **Global hotkey via AutoHotkey** — Focus/launch the app from Windows (WSL2).
5. **Robust GUI** — PyQt6-based, dark-themed, reliable on Linux/WSL2.
6. **Single installation pipeline** — One `install.sh` that works on WSL2, Linux, and macOS.

---

## Target Architecture

```
automatr/
├── automatr/                # Main Python package
│   ├── __init__.py
│   ├── __main__.py          # CLI entry point
│   ├── core/                # Core logic (no external integrations)
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration management
│   │   └── templates.py     # Template loading/saving (JSON only)
│   ├── ui/                  # PyQt6 GUI
│   │   ├── __init__.py
│   │   ├── main_window.py   # Main application window
│   │   ├── template_editor.py
│   │   └── theme.py         # Dark theme setup
│   └── integrations/        # External system integrations
│       ├── __init__.py
│       ├── llm.py           # llama-server process + HTTP client
│       ├── espanso.py       # Espanso YAML generation
│       └── ahk.py           # AutoHotkey script management
├── scripts/
│   ├── launch.ahk           # Windows global hotkey script
│   └── migrate_templates.py # One-off migration from old repo
├── templates/               # Default/example templates (JSON)
│   └── example.json
├── install.sh               # Unified installer
├── pyproject.toml           # Python project metadata
├── README.md
└── PLAN.md                  # This file
```

---

## Template Schema (JSON)

Each template file is a single JSON object:

```json
{
  "name": "Code Review",
  "description": "Ask an LLM to review code.",
  "trigger": ":review",
  "variables": [
    { "name": "language", "label": "Programming Language", "default": "Python" },
    { "name": "code", "label": "Code Snippet", "multiline": true }
  ],
  "content": "Please review the following {{language}} code:\n\n```\n{{code}}\n```\n\nProvide feedback on correctness, style, and potential improvements."
}
```

- **name**: Display name.
- **description**: Short description (optional).
- **trigger**: Espanso trigger string (optional, e.g., `:review`).
- **variables**: List of variable definitions.
  - `name`: Variable key (used in `{{name}}` placeholders).
  - `label`: Human-readable label for the UI.
  - `default`: Default value (optional).
  - `multiline`: Boolean, true for text areas (optional).
- **content**: The prompt template with `{{variable}}` placeholders.

---

## GUI Framework: PyQt6

**Rationale:**
- Native look and feel on Linux/WSL2/macOS.
- Excellent dark mode support (via `qdarktheme` or similar).
- Robust window management (focus, snapping, resizing).
- Mature, well-documented, widely used.

**Alternatives Rejected:**
- *Tkinter*: Outdated appearance, limited theming, focus issues.
- *Textual/TUI*: Doesn't meet "real app" GUI requirement.
- *Web-based (Flet/NiceGUI)*: Browser overhead, less native integration.

---

## Local Model Integration

- Use `llama.cpp`'s `llama-server` binary.
- **Build from source** by default for optimal performance (AVX, CUDA).
- HTTP client sends prompts to `http://localhost:8080/completion`.
- Robust error handling: health checks, timeouts, clear messages.
- Model discovery: User-configured path, with recursive search for `.gguf` files.

---

## Espanso Integration

- Read templates with a `trigger` field.
- Generate a single `automatr.yml` match file.
- Place it in the Espanso user config directory.
- UI button: "Sync to Espanso" to regenerate.
- WSL2: Optionally write to the Windows Espanso path.

---

## AutoHotkey Integration

- Minimal `launch.ahk` script.
- Default hotkey: `Ctrl+Shift+J`.
- Action: Focus existing window or launch via `wsl.exe`.
- Installer places the script in a known location; user runs it at startup.

---

## Unified Installer (`install.sh`)

1. Detect OS: Linux, WSL2, macOS.
2. Install system dependencies:
   - Linux/WSL2: `qt6-base-dev`, `build-essential`, `cmake`.
   - macOS: Xcode CLI tools, Homebrew dependencies.
3. Clone and build `llama.cpp` from source.
4. Create Python virtual environment.
5. Install Python dependencies (`PyQt6`, `requests`, `pyyaml`).
6. Copy default templates.
7. Generate initial configuration.
8. Run smoke test (imports, binary presence, config write).

---

## CLI Entry Points

| Command              | Description                                  |
|----------------------|----------------------------------------------|
| `automatr`           | Launch the GUI.                              |
| `automatr --sync`    | Regenerate Espanso match file from templates.|
| `automatr --version` | Print version and exit.                      |

No other flags. Keep it minimal.

---

## Features Explicitly Excluded

The following are **not** part of Automatr and must not be carried over:

- MCP servers
- Obsidian integration
- Todoist integration
- SQLite database for templates
- Complex packagers (pipx wrappers, Docker, etc.)
- Multi-platform native installers (Windows `.exe`, macOS `.app`)
- Advanced CLI modes (background daemons, complex flags)
- Plugin discovery/loading infrastructure (keep integrations hardcoded)
- Any cloud service or external API (except local `llama-server`)

---

## Implementation Phases

### Phase 0: Documentation (This File)
- [x] Write comprehensive plan.

### Phase 1: Analyze & Exclude
- [x] Audit `prompt-automation` for features to exclude.
- [x] Identify exact logic to reference for templates, LLM, Espanso.
- [x] Document findings in `docs/PHASE1_ANALYSIS.md`.

### Phase 2: Core Architecture & Data Layer
- [x] Initialize `automatr` package structure.
- [x] Implement `TemplateManager` (JSON CRUD).
- [x] Implement `ConfigManager`.

### Phase 3: Local Model Engine
- [x] Implement `llama-server` process manager.
- [x] Implement HTTP client with health checks.
- [x] Add model discovery logic.

### Phase 4: GUI Implementation
- [x] Create main window (3-pane layout).
- [x] Implement template list view.
- [x] Implement variable form.
- [x] Implement output/preview pane.
- [x] Add dark theme.

### Phase 5: Espanso & AutoHotkey
- [x] Implement Espanso YAML generator.
- [x] Add "Sync to Espanso" UI action.
- [x] Create `launch.ahk` script.

### Phase 6: Unified Installer
- [x] Write `install.sh` for WSL2/Linux/macOS.
- [x] Add smoke test.
- [x] Document installation in README.

### Phase 7: Migration & Polish
- [x] Create template migration script.
- [x] Write user documentation.
- [ ] Final testing and hardening.

---

## Quality Attributes

- **Stability**: Predictable behavior, clear errors, no silent failures.
- **Simplicity**: Fewest moving parts, no unnecessary abstractions.
- **Maintainability**: Clear separation of concerns, easy to modify.
- **Developer Ergonomics**: Run from source, immediate feedback, easy template editing.

---

## Next Steps

Proceed to **Phase 1: Analyze & Exclude** to identify what to carry over from the original repository.
