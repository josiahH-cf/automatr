"""Automatr CLI entry point."""

import argparse
import sys

from automatr import __version__


def main() -> int:
    """Main entry point for automatr CLI."""
    parser = argparse.ArgumentParser(
        prog="automatr",
        description="Minimal prompt automation tool with local LLM integration",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"automatr {__version__}",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Sync templates to Espanso and exit",
    )

    args = parser.parse_args()

    if args.sync:
        from automatr.integrations.espanso import sync_to_espanso

        success = sync_to_espanso()
        return 0 if success else 1

    # Default: launch GUI
    from automatr.ui.main_window import run_gui

    return run_gui()


if __name__ == "__main__":
    sys.exit(main())
