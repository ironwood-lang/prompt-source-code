# PromptSourceCode 0.1.0

PromptSourceCode 0.1.0 is the first public release.

It keeps the human conversation behind an AI-assisted project alongside the work itself:
initial requests, follow-ups, steering, corrections, outcomes, and preserved attachments.

## Start here

1. Download and unzip the source archive attached to this release.
2. Copy `templates/AGENTS.prompt-source-standard.md` into the root of a new project as
   `AGENTS.md`, or append the complete template to an existing root `AGENTS.md`.
3. Open the project in Codex Desktop and start a new task.
4. Follow the example in the
   [README](https://github.com/ironwood-lang/prompt-source-code/blob/v0.1.0/README.md) and
   look for `PROMPT_SOURCE.md` in the project root.

The standard installation is complete on its own. Optional local hooks are available for
advanced users who want stronger prompt matching and trusted interruption capture.

## Included

- chronological capture of initial prompts, follow-ups, steering, and corrections;
- readable results and explicit unfinished or interrupted states;
- flat, byte-preserving artifact snapshots when source files are available;
- an optional local hook enhancement that remains inert until explicitly reviewed,
  enabled, and trusted;
- installation, upgrade, compatibility, troubleshooting, and technical documentation;
  and
- deterministic regression tests plus clean-project Codex Desktop acceptance evidence.

## Supported scope

Release 0.1.0 supports the tested local Codex Desktop workflow on macOS. Standard capture
does not require hooks, a plugin, a skill, a background service, Python, or a network
service. Optional hooks use the tested macOS system Python environment.

Codex CLI is used only to review and trust optional hooks; it is not a supported capture
environment. Windows, Linux, the Codex IDE extension, cloud capture, and other coding
agents are not claimed as supported in this release.

## More information

- [End-user installation and troubleshooting](https://github.com/ironwood-lang/prompt-source-code/blob/v0.1.0/docs/INSTALLATION.md)
- [Compatibility and upgrade policy](https://github.com/ironwood-lang/prompt-source-code/blob/v0.1.0/docs/COMPATIBILITY.md)
- [Technical reference](https://github.com/ironwood-lang/prompt-source-code/blob/v0.1.0/docs/TECHNICAL_REFERENCE.md)
- [0.1.0 release-readiness evidence](https://github.com/ironwood-lang/prompt-source-code/blob/v0.1.0/docs/CODEX_DESKTOP_V1_RELEASE_READINESS.md)
