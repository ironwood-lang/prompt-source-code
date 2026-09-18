# PromptSourceCode Compatibility and Upgrade Policy

## Two different compatibility questions

**Format compatibility** asks whether a reader or writer understands the bytes and
semantics of a `PROMPT_SOURCE.md` history. **Capture-environment support** asks whether a
particular Codex host, operating system, filesystem, Python runtime, and Git workflow have
been exercised end to end. A format-compatible history does not imply that every
environment is supported for live capture.

PromptSourceCode 0.2.0 is the product release. Schema 1 is the storage-format version.
Those version numbers are intentionally independent.

## Schema-1 format compatibility

Schema-1 histories begin with the exact first line:

```text
<!-- prompt-source-schema: 1 -->
```

Schema 1 is frozen by [`PROMPT_SOURCE_FORMAT.md`](PROMPT_SOURCE_FORMAT.md). A compatible
schema-1 implementation must preserve existing entry order, immutable captured fields,
artifact bytes, and the two-output storage topology. Missing entry numbers remain missing;
valid histories are never renumbered merely to become contiguous.

The schema number is the format compatibility boundary, not the PromptSourceCode product
release number. Documentation clarifications, test additions, and implementation fixes
may remain schema 1 only when they do not change the interpretation of valid schema-1
bytes or make a valid schema-1 history invalid. A change to required topology, field
meaning, payload reconstruction, lifecycle semantics, or artifact fidelity requires a
new schema marker and explicit migration guidance.

Writers must stop without modifying a history that has an absent, malformed, truncated,
incompatible, or future schema marker. They also stop on malformed fences, duplicate or
non-increasing structural headings, stale optimistic digests, and other structural
conflicts. Schema 1 never treats an unknown schema as an empty history and never silently
upgrades it.

## Tested capture environments

Release evidence establishes the following environments:

| Path | Tested environment | Evidence |
| --- | --- | --- |
| Standard capture | Codex Desktop 26.908.70816 (9275), macOS 26.6.2 (25G83), local Git project | [Milestone 2 validation](CODEX_DESKTOP_STANDARD_CAPTURE_VALIDATION.md) |
| Optional hooks | Codex Desktop 26.911.61220 (9647), macOS 26.6.2 (25G83), `/usr/bin/python3` 3.9.6, local Git project | [Milestone 3 validation](CODEX_DESKTOP_HOOK_CAPTURE_VALIDATION.md) |
| Final 0.1.0 bundle | Codex Desktop / ChatGPT app 26.911.61220 (9647), macOS 26.6.2 (25G83), `/usr/bin/python3` 3.9.6, Git 2.54.0 (Apple Git-157), local Git project | [0.1.0 release readiness](CODEX_DESKTOP_V1_RELEASE_READINESS.md) |
| 0.2.0 standard capture and optional-hook repair | Codex Desktop 26.915.31029 (9771), GPT-5.6 SOL Medium, macOS 26.6.2 (25G83), `/usr/bin/python3` 3.9.6, Git 2.54.0 (Apple Git-157), local Git project | [Milestone 6 combined-evidence signoff](MILESTONE_6_SIGNOFF_20260918.md) |

The historical 0.1.0 standard capture had no Python runtime dependency. Release 0.2.0
requires the system Python for its project-local capture helper. The optional implementation is tested
with the system Python listed above and uses macOS/POSIX file locking and atomic local
filesystem replacement. Git is used for the captured project's ordinary workflow and
project discovery; hooks themselves execute no Git commands.

These results support PromptSourceCode 0.2.0 for the tested local Codex Desktop on macOS
workflow. They do not claim that every later Desktop, macOS, Python, or Git version
behaves identically.

The 0.2.0 signoff combines FULL_01's passing cases with actual Desktop retests of its two
failures after repair, plus automated regression checks. It does not claim a single
all-green full Desktop run on the final candidate; the owner accepted this evidence basis.

## Untested environments and 0.2.0 non-goals

Release 0.2.0 does not claim capture-environment support for:

- Codex CLI, except using `/hooks` to review, enable, disable, and trust optional hooks;
- the Codex IDE extension, Codex cloud, ChatGPT cloud tasks, or remote capture;
- Windows, Linux, network filesystems, or filesystems without the tested POSIX locking and
  atomic-replacement behavior;
- Claude Code or any other coding agent;
- a skill, plugin, background service, or network service as a required capture path; or
- automatic publication or synchronization of generated provenance.

A schema-1 history may still be readable on an untested platform. That is format
compatibility, not evidence of supported live capture.

## Upgrade within schema 1

The full-inline 0.1.0 installation is a pre-1.0 experiment and is not retained as a second
capture layout. Follow the [0.1.0 replacement steps](INSTALLATION.md#3-update-the-loader-and-dedicated-instructions)
to remove the complete old block before installing the compact loader from
[`AGENTS.prompt-source-loader.md`](../templates/AGENTS.prompt-source-loader.md), and install
[`prompt-source-instructions-v1.md`](../templates/prompt-source-instructions-v1.md) at the
frozen project path `.prompt-source/instructions-v1.md`, with the matching project-local
validator at `.prompt-source/validate.py`. For an existing compact-loader installation,
the documented `scripts/instruction_contract.py update` operation preserves all root
content outside the loader, every nested `AGENTS.md`, and existing schema-1 provenance.

If capture was disabled, restore that state after the update unless re-enabling is
intentional. The layout uses no user-specific global Codex configuration, fallback
filename, skill, plugin, hook, service, or network dependency.

Start a new Desktop task after updating so it receives the current loader. Subsequent
enable/disable changes are reread from disk on each submission. A reliably exposed
`CODEX_THREAD_ID` may populate schema 1's existing optional `Session ID`; it is not
hook-only metadata. Older entries without that value remain unchanged and valid.

Do not rewrite, renumber, normalize, or recreate existing schema-1 entries. Preserve
`PROMPT_SOURCE.md` and all verified files in `prompt_source_assets/`. New captures append
after the greatest valid structural entry number.

For optional hooks:

1. disable both definitions and restart Desktop;
2. replace both Python files and the two configuration groups from the reviewed release;
3. review, enable, and trust `UserPromptSubmit` and `Interrupt` separately through CLI
   `/hooks`; and
4. fully restart Desktop before testing in a new Desktop task.

Modifying a command or handler property invalidates the prior decision because any
definition edit changes the hash-bound trust decision. The tested CLI may not display the
raw hash; review the exact definition and do not invent a hash or bypass trust.

## Encountering another schema

If the first line is not `<!-- prompt-source-schema: 1 -->`, preserve the history and its
assets unchanged and stop schema-1 writes. Determine which PromptSourceCode version owns
that schema before taking further action. Do not prepend a schema-1 header, copy entries
into a new file, or reuse schema-1 hook helpers against the unknown history.

A future PromptSourceCode release may provide explicit migration instructions or a
separately validated migration tool. PromptSourceCode 0.2.0 makes no promise that such a
tool exists and performs no automatic migration. Any future migration must preserve the
original history and artifacts until the user deliberately accepts a documented
conversion.
