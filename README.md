# Automatr

Prompt templates + local LLM in one GUI. No cloud, no API keys.

## Install & Run

```bash
./install.sh    # builds llama.cpp, sets up Python venv
automatr        # launch GUI
```

**Requirements:** Linux/WSL2, Python 3.10+, a `.gguf` model in `~/models/`

## What It Does

1. **Pick a template** — reusable prompts with `{{variables}}`
2. **Fill in the blanks** — GUI form for each variable
3. **Generate** — local llama.cpp server, GPU-accelerated
4. **Copy result** — paste anywhere

Templates sync to [Espanso](https://espanso.org) for system-wide text expansion.

## Files

```
~/.config/automatr/
├── config.json      # model path, port, theme
└── templates/       # your prompt templates (JSON)
```

## License

MIT
