#!/usr/bin/env python3
"""Entry point copied into an opted-in project's .codex/hooks directory."""

from prompt_source_core import main


if __name__ == "__main__":
    raise SystemExit(main())
