# Automatr

Prompt templates + local LLM in one GUI. No cloud, no API keys.

## Install & Run

```bash
./install.sh    # builds llama.cpp, sets up Python venv
automatr        # launch GUI
```

**Requirements:** 
- Linux, WSL2, or macOS
- Python 3.10+
- A `.gguf` model in `~/models/`
- **macOS only:** [Homebrew](https://brew.sh) (`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`)

## Get a Local Model

Automatr uses local models so everything runs on your machine—no internet, API keys, or subscriptions.

1. In the app, go to **LLM → Download Models (Hugging Face)** to browse models
   - Look for `.gguf` files (optimized for llama.cpp)
   - Start with smaller models (3-8B parameters) for faster performance

2. After downloading, go to **LLM → Select Model → Add Model from File...** and select your `.gguf` file

The model is copied to `~/models/` and ready to use.

## Windows Hotkey (WSL2)

Press **Ctrl+Shift+J** anywhere in Windows to launch Automatr.

The installer automatically:
- Creates an AutoHotkey script in `Documents/AutoHotkey/automatr.ahk`
- Adds it to Windows Startup so it runs on boot

**Requires:** [AutoHotkey v1.1](https://www.autohotkey.com/download/ahk-install.exe) (free, ~3MB)

If AutoHotkey is already installed, just double-click `automatr.ahk` to enable the hotkey.

## What It Does

1. **Pick a template** — reusable prompts with `{{variables}}`
2. **Fill in the blanks** — GUI form for each variable
3. **Generate** — local llama.cpp server, GPU-accelerated
4. **Copy result** — paste anywhere

Templates sync to [Espanso](https://espanso.org) for system-wide text expansion.

## Files

**Linux/WSL:**
```
~/.config/automatr/
├── config.json      # model path, port, theme
└── templates/       # your prompt templates (JSON)
```

**macOS:**
```
~/Library/Application Support/automatr/
├── config.json
└── templates/
```

## License

MIT
