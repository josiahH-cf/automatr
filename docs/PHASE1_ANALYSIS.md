# Phase 1: Analyze & Exclude

This document details the analysis of the original `prompt-automation` repository to identify:
1. Features to **carry over** (minimal, essential logic).
2. Features to **exclude** (not part of the minimal core).

---

## Repository Structure Overview

The original repository is large and complex:
- **70+ Python modules** across `src/prompt_automation/`
- Multiple integration points: Espanso, AutoHotkey, Obsidian, Todoist, MCP, etc.
- Complex installer scripts for Windows, macOS, Linux, and WSL2
- SQLite-backed template indexing with search
- Version control for templates

---

## Features to CARRY OVER (Reference Only)

### 1. Template System

**Source Files to Reference:**
- `src/prompt_automation/types.py` — Template TypedDict schema
- `src/prompt_automation/templates/__init__.py` — TemplateManager (CRUD)
- `src/prompt_automation/renderer.py` — `fill_placeholders()` function

**Key Schema (from `types.py`):**
```python
class Placeholder(TypedDict, total=False):
    name: str
    label: NotRequired[str]
    default: NotRequired[str]
    multiline: NotRequired[bool]

class Template(TypedDict, total=False):
    id: int
    title: str
    style: str
    template: List[str]
    placeholders: List[Placeholder]
    metadata: NotRequired[Dict[str, Any]]
```

**Simplification for Automatr:**
- Remove `id` (use filename as identifier).
- Remove `style` (not needed for minimal version).
- Add `trigger` field for Espanso.
- Store as single JSON file, not directory + SQLite.

**Automatr Template Schema:**
```json
{
  "name": "Code Review",
  "description": "Ask an LLM to review code.",
  "trigger": ":review",
  "variables": [
    { "name": "language", "label": "Language", "default": "Python" },
    { "name": "code", "label": "Code", "multiline": true }
  ],
  "content": "Review this {{language}} code:\n{{code}}"
}
```

---

### 2. Local LLM Server

**Source File to Reference:**
- `src/prompt_automation/services/llm_server.py` — `LLMServerService`

**Key Logic:**
- Finds `llama-server` binary via multiple candidate paths.
- Constructs command: `llama-server --model <path> --port 8080 --ctx-size 2048 --n-gpu-layers N`.
- Manages process lifecycle (start/stop).
- Checks port status via `psutil`.

**Simplification for Automatr:**
- Single config file for model path and server port.
- Simple binary finder (PATH + config).
- HTTP client for `/completion` endpoint.
- Clear error messages when binary or model is missing.

---

### 3. Espanso Sync

**Source File to Reference:**
- `src/prompt_automation/espanso_sync.py` — Main sync orchestrator

**Key Logic:**
- Reads templates from `espanso-package/templates/` and `espanso-package/match/`.
- Generates YAML match files with `trigger` and `replace` fields.
- Detects WSL2 and handles Windows Espanso path.
- Restarts Espanso daemon after sync.

**Simplification for Automatr:**
- Read templates from `~/.automatr/templates/`.
- Filter templates with a `trigger` field.
- Generate a single `automatr.yml` file.
- Place in Espanso config directory.
- Simple daemon restart.

---

### 4. AutoHotkey

**Source Files to Reference:**
- `scripts/prompt-automation.ahk` — Windows global hotkey

**Key Logic:**
- Hotkey: `Ctrl+Shift+J`
- Checks if window with title "Prompt Automation" exists.
- If exists, focus it. If not, launch via `prompt-automation.exe --gui` or `python -m prompt_automation`.

**Simplification for Automatr:**
- Single `launch.ahk` script.
- Hotkey: `Ctrl+Shift+A` (configurable).
- Focus or launch `wsl.exe -e automatr`.

---

## Features to EXCLUDE

### Integrations (Remove Entirely)
| Feature | Location | Reason |
|---------|----------|--------|
| Obsidian | `src/prompt_automation/gui/obsidian/` | Not core; cloud-like |
| Todoist | `src/prompt_automation/services/todoist_action.py` | Not core; cloud |
| MCP Servers | `src/prompt_automation/plugins/mcp/` | Not core; complex |
| Reminders | `src/prompt_automation/reminders.py` | Not core |
| Notes | `src/prompt_automation/notes/` | Not core |
| Recommendations | `src/prompt_automation/recommendations/` | Not core |
| Analytics | `src/prompt_automation/analytics/` | Not core |
| Knowledge | `src/prompt_automation/knowledge/` | Not core |

### Complex Subsystems (Remove Entirely)
| Feature | Location | Reason |
|---------|----------|--------|
| SQLite indexing | `templates/__init__.py` (conn) | Overkill; use filesystem |
| Template versioning | `templates/versions.py` | Overkill; use git |
| Search engine | `services/search_engine.py` | Overkill; list all |
| Cache system | `cache/` | Premature optimization |
| Error recovery | `error_recovery/` | Overengineered |
| Dashboard | `dashboard/` | Not core |
| Workspace | `workspace/` | Not core |
| Context | `context/` | Not core |
| Starred | `starred.py` | Not core |
| History | `history.py` | Not core |

### Complex Installers (Remove Entirely)
| Feature | Location | Reason |
|---------|----------|--------|
| Windows PowerShell installer | `install/install-windows.ps1` | WSL2-focused |
| macOS installer | `install/install-mac.sh` | Keep minimal support |
| Espanso migration | `install/espanso_migration.sh` | Legacy |
| Orchestrator | `install/orchestrator.py` | Overengineered |

### CLI Complexity (Remove Entirely)
| Feature | Reason |
|---------|--------|
| `--espanso-sync` | Reduce to `--sync` |
| `--background-hotkey` | Not needed |
| `--focus` | Handle in GUI |
| `--selector` | Single GUI mode |
| `--no-gui` | Always GUI |
| Config flags | Use config file |

### GUI Complexity (Remove Entirely)
| Feature | Location | Reason |
|---------|----------|--------|
| Template browser | `templates/browser.py` | Simplify to list |
| Wizard | `gui/wizard/` | Simplify to form |
| Collector | `gui/collector/` | Not core |
| Popup window | `gui/popup_window/` | Single window |
| Single window KB | `gui/single_window/` | Simplify |
| Accessibility features | `gui/accessibility/` | Defer |
| Visual feedback | `gui/visual_feedback/` | Defer |

---

## Summary: What to Re-Implement

| Component | Lines of Code (Est.) | Priority |
|-----------|---------------------|----------|
| Template JSON loader | ~50 | P0 |
| Template variable substitution | ~30 | P0 |
| Config manager | ~40 | P0 |
| LLM server manager | ~100 | P0 |
| LLM HTTP client | ~50 | P0 |
| Espanso YAML generator | ~60 | P1 |
| PyQt6 main window | ~200 | P0 |
| PyQt6 template list | ~80 | P0 |
| PyQt6 variable form | ~100 | P0 |
| PyQt6 output pane | ~60 | P0 |
| AutoHotkey script | ~20 | P1 |
| Install script | ~100 | P1 |

**Total Estimated: ~900 lines** (vs. original ~15,000+ lines)

---

## Next Step

Proceed to **Phase 2: Core Architecture & Data Layer** to implement:
1. `automatr/core/config.py` — Configuration management
2. `automatr/core/templates.py` — Template loading/saving (JSON only)
3. Basic directory structure
