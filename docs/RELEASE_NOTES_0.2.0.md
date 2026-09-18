# PromptSourceCode 0.2.0

PromptSourceCode 0.2.0 introduces a smaller `AGENTS.md` installation and deterministic
helpers for recording history, results, and attachments. Hooks remain optional.

## Install

Requires Codex Desktop on macOS, a local Git project, and `/usr/bin/python3` (tested with
Python 3.9.6). No additional Python packages are needed.

1. Download **Source code (zip)** from the
   [0.2.0 release](https://github.com/ironwood-lang/prompt-source-code/releases/tag/v0.2.0)
   and unzip it.
2. Open Terminal in the extracted `prompt-source-code-0.2.0` folder and run:

   ```sh
   /usr/bin/python3 scripts/instruction_contract.py install "/path/to/your/project"
   /usr/bin/python3 scripts/instruction_contract.py check "/path/to/your/project"
   ```

3. Review the loader appended to your project's `AGENTS.md` and the two installed files,
   `.prompt-source/instructions-v1.md` and `.prompt-source/validate.py`.
4. Open the project in Codex Desktop and start a new task. The agent reads the capture
   instructions through `AGENTS.md` and uses the local helper while doing ordinary work.

This is the complete standard installation. It does not install or activate hooks or
require a skill, plugin, background service, global Codex configuration, or network service.
The [installation guide](INSTALLATION.md) covers updates, disabling, and removal.

## What's changed since 0.1.0

- The always-read instructions shrink from 2,591 words / 18,250 bytes to 962 words /
  7,652 bytes combined. The root loader itself is 196 words / 1,523 bytes.
- The full operational contract lives at `.prompt-source/instructions-v1.md`. Existing
  root and nested project guidance remains in place.
- The standard Python helper checks live capture controls, writes entries atomically,
  preserves artifacts, renders changed-file reports, and validates history structure.
- Artifact names, classification, source-byte checks, and pasted-image fidelity are
  handled consistently by the helper.
- Optional hook completion requires explicit interaction classification and correction
  targets. Recognized Desktop attachment envelopes are separated before user input is
  captured and made immutable.

**Python is now required for standard capture too.** Version 0.1.0's standard path did
not use Python; 0.2.0 asks the agent to run the project-local helper. Hooks are still a
separate opt-in enhancement with explicit review and trust.

## Updating an existing project

For the old 0.1.0 full-inline installation, remove only its complete marked block before
installing the new layout. For an existing compact loader, use `instruction_contract.py
update`. Follow the [step-by-step update procedure](INSTALLATION.md#3-update-the-loader-and-dedicated-instructions)
so both capture contracts are not left active together.

Keep `PROMPT_SOURCE.md` and `prompt_source_assets/` untouched. Product version 0.2.0 still
uses storage schema 1 and instruction version 1; existing valid history is not migrated,
renumbered, or rewritten. These fixes apply to future captures, not retroactive repairs.
Disable optional hooks before updating them, then review, enable, and trust both definitions
through CLI `/hooks` and restart Desktop. See [optional hooks](OPTIONAL_HOOKS.md).

## Validation and support

Milestone 6 is signed off using the owner-approved combination of FULL_01's passing
Desktop cases, successful actual H07/H08 Desktop retests after repair, and automated
regression checks. The original full-validator failure remains preserved. This release
does not claim that every case was repeated in one successful full run on the repaired
candidate. The [signoff record](MILESTONE_6_SIGNOFF_20260918.md) explains the evidence and
the accepted exception to that original gate.

Support remains the tested local Codex Desktop workflow on macOS, using GPT-5.6 SOL,
Medium in the acceptance runs. Standard capture remains model-mediated. Artifact fidelity
covers the exposed source bytes, and pasted images cover Desktop's materialized image,
not an unknown pre-clipboard original. Generated history stays local and unstaged unless
you explicitly ask to include it in Git or share it.

Codex CLI is used only for optional-hook review and trust; CLI capture, the IDE extension,
cloud tasks, Windows, Linux, and other agents remain outside the tested support scope.
See [compatibility](COMPATIBILITY.md) for the full boundary.
