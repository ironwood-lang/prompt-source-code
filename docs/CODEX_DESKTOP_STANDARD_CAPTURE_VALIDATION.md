# Codex Desktop Standard-Capture Validation

This is the preserved Milestone 2 evidence for the standard path. The frozen 0.1.0
bundle was later rechecked in the separate
[`CODEX_DESKTOP_V1_RELEASE_READINESS.md`](CODEX_DESKTOP_V1_RELEASE_READINESS.md) run;
that later report does not alter the facts recorded here.

## Environment and scope

Validation completed on 2026-09-16 in Codex Desktop 26.908.70816 (9275) on macOS
26.6.2 (25G83). The full-case disposable project ran at the local Git repository
`~/Vibe/PSC_Test` and was preserved after the run as
`~/Vibe/PSC_Test_M2_validation_and_append_defect_20260916`; its local bare
test remote was preserved as `PSC_M2_full_validation_origin_20260916.git`. The pre-existing
feasibility project formerly at that location was preserved intact as
`PSC_Test_M0_backup_20260916` before the clean repository was initialized.

The disposable repository began with only a root `AGENTS.md` copied byte-for-byte from
the standard template and committed as `70f0c85`. It had no `.codex` directory or
repository hook configuration. The capture task used no PromptSourceCode hook, skill,
plugin, background service, or network dependency. Codex task-management tools created,
continued, and inspected the Desktop task; a human used the Desktop UI for real file
attachments, image paste, and the Stop button.

The first captured submission created `PROMPT_SOURCE.md` before requested project work.
At the required-case checkpoint, the history contained structural Entries `000001`
through `000015` in physical order. Later lifecycle hardening is reported separately
below because it deliberately continued the project after that checkpoint.

## Results

| Case | Outcome | Evidence |
| --- | --- | --- |
| First-prompt initialization | Pass | Entry `000001` was written as `In progress` before `src/complex.txt`; the Desktop task trace records the history file change before the task-work file change. |
| Complex text and newline states | Pass at the agent-visible boundary | Entry `000001` retained leading and trailing spaces, consecutive spaces, tabs, blank lines, Unicode, Markdown, nine-backtick and eleven-tilde fences, and heading/schema-like text inside a ten-backtick outer fence. Its known ending was `LF`. Entry `000002` had the known ending `None`. Desktop delivered the HTML-like comment as `&lt;!-- ... --&gt;`, and the history correctly retained that delivered representation instead of reversing it. |
| Normal follow-up | Pass | Entry `000002` followed completed Entry `000001` and remained separate. |
| Two messages steering one active turn | Pass | Entries `000004` and `000005` were written separately and in order during the same active Desktop turn before the badge work was finalized. |
| Superseding correction | Pass | Entry `000006` uses `Interaction: Correction` and `Supersedes: Entry 000004`; the earlier blue instruction remains unchanged. |
| Completed prompt with no task-work change | Pass | Entries `000002`, `000008` through `000012`, and `000015` use `Changed files: None.` where applicable. |
| Attached binary file | Pass | Entry `000010`; source and copy were each 1,266,984 bytes with SHA-256 `b536084ff3cb9348e6a4a2f3fbb18eeab643ae2c50295dacedb2591e53665ac6`; `cmp` returned success. |
| Attached images | Pass | Entry `000011`; the first source/copy pair was 1,192,930 bytes with SHA-256 `987021540010256dbc2ee5f722ff21b75657744d5f40cbee3c8dd049cb34eb4a`, and the second was 1,433,435 bytes with SHA-256 `d11aff3b59211a894e7e28f45df59e24de960f563e43e317931f83c2b3e5c8f6`. Both `cmp` checks succeeded. |
| Pasted image | Pass with the documented fidelity boundary | Entry `000012`; the Desktop temporary PNG and captured copy were each 1,433,435 bytes with SHA-256 `d11aff3b59211a894e7e28f45df59e24de960f563e43e317931f83c2b3e5c8f6`; `cmp` returned success. The pre-clipboard PNG was 1,192,930 bytes with SHA-256 `987021540010256dbc2ee5f722ff21b75657744d5f40cbee3c8dd049cb34eb4a`, so binary identity was correctly not claimed. Both decoded to 1254 by 1254 RGB images; normalized BMP raster payloads were byte-identical with SHA-256 `ffab4111999c1680286677716239a88a747c0588fd9de10b74e9d6cfcfc37d19`. |
| Sanitization and collision | Pass | Two differing images named `Résumé Final ??.PNG` were attached in the same interaction. They became `prompt-000011-R-sum-Final.png` and `prompt-000011-R-sum-Final-002.png`; neither payload was overwritten. |
| Repository-local source | Pass | Entry `000008` copied `fixtures/repository source.txt` to a flat point-in-time snapshot. Source and copy were each 33 bytes with SHA-256 `48632bebf3354e581a450486900c5d9a022a70c3d011e6b7c89afab3664048eb`. |
| Unavailable external artifact | Pass | Entry `000009` records `Preservation: Unavailable` and `Unavailable reason: Unknown`, with no link, byte count, digest, placeholder, or invented explanation. |
| Real interruption and later recovery | Pass | A first timing attempt completed because Stop was not pressed and remains honestly recorded as completed Entry `000013`. During the repeated attempt, Entry `000014` existed as `In progress`, the user pressed Stop in Desktop, and the requested marker file was absent. Standard capture did not add a result or infer `Interrupted`. Entry `000015` later converted Entry `000014` to `Incomplete` with the canonical unknown-reason text. No history entry uses `Interrupted`. |
| Final structure | Pass | One root `PROMPT_SOURCE.md`, one flat `prompt_source_assets/` with five direct-child files, unique ordered structural Entries `000001`–`000015`, no per-prompt directories, and no separate input, result, status, or runtime-context files. A heading-like `Entry 999999` inside fenced input remained data. |
| Git behavior | Pass | Ordinary files were explicitly staged, committed as `105fdf0`, and pushed to the local bare `origin/main`. During and after that operation, `PROMPT_SOURCE.md` and `prompt_source_assets/` remained untracked and absent from the index and remote tree. The generated outputs were not committed, pushed, published, or uploaded. |

## What is independently checked

The source/copy sizes, SHA-256 digests, `cmp` results, repository tree, Git index, remote
tree, file topology, entry headings, status values, and normalized image raster comparison
were checked with deterministic local tools outside the capture agent's prose. Those are
independent byte-level or structural checks.

Text reproduction is different. The agent observed the representation delivered by Codex
Desktop and wrote it to the history. The Desktop transcript and stored payload were then
inspected, but that model-mediated observation and read-back are not independent proof of
equality with pre-serialization keystrokes or editor state. The HTML entity transformation
in Entry `000001` is direct evidence of that boundary.

## Release-candidate hardening

The run and post-run lifecycle check exposed three deterministic ambiguities in the
Milestone 1 validation contract:

1. The collision checklist did not require both colliding names to occur in the same
   entry. Because the entry number is part of every asset name, separate entries do not
   exercise suffixing. The checklist and fixture now require a same-entry collision and
   automated coverage verifies the `-002` payload is different.
2. The pasted-image fidelity sentence was specified as exact prose but could wrap across
   physical Markdown lines, as it did in Entry `000012`. The format and template now
   require one physical field line, backed by an automated check.
3. A post-run task selected the correct number `000016` but inserted its block after an
   earlier repeated result marker instead of physical EOF. The format and template now
   require pre-write physical-order validation, EOF-only append, and post-write
   verification before task work. A newly misplaced unfinished block may be moved to EOF
   only when its exact boundary is known. The automated contract checks require these
   safeguards.

Release-candidate lifecycle work also added explicit template begin/end markers, an
enabled/disabled capture control, and installation, update, disable, re-enable, instruction
removal, generated-data removal, and Git-policy guidance. The README now states explicitly
that default Git exclusion is agent behavior, not an automatic `.gitignore` rule.

## Post-run lifecycle and append validation

With the final control block installed, an enabled interaction was captured, the next
captured interaction changed only `- Capture: enabled` to `- Capture: disabled`, and a new
Desktop task ran while disabled. The history stayed byte-for-byte unchanged at 13,907
bytes with SHA-256 `99b4c577bc388f48124ce075152ebdaebfff7f847084eac480f116a4390dfeb6`.
Re-enabling from the disabled task also preserved the history unchanged.

The first cross-task update exposed the misplaced-append defect described above. That
project was preserved without silently rearranging the captured history. A second clean
repository was then initialized at `~/Vibe/PSC_Test` with local commit
`db3a495` and bare remote `PSC_M2_append_fix_origin.git`. Two interactions in one Desktop
task produced ordered Entries `000001` and `000002`, both with repeated
`Changed files: None.` results. A new Desktop task initially misplaced Entry `000003` after
a repeated marker; the mandatory post-write check detected the fault before task work,
moved only the new unfinished block to physical EOF, re-ran the invariant, and completed
with structural headings `000001`, `000002`, `000003` in strictly increasing physical
order.

## Remaining limitations and deferred work

- Standard capture is model-mediated and cannot independently prove text equality at the
  Desktop delivery boundary.
- Standard capture cannot distinguish a Stop-button interruption from exit, crash,
  shutdown, or another unfinished cause. Only a trusted optional hook may use `Interrupted`.
- Instruction-mediated capture does not provide multi-writer locking or crash-safe atomic
  writes. Those protections and hook/agent deduplication were deferred to and subsequently
  completed for optional hook writes in Milestone 3; they do not change this standard-path
  limitation.
- This run establishes support only for the tested Codex Desktop and macOS versions. It
  does not establish Codex CLI, IDE extension, cloud, or other-agent support.
- The clarified one-line fidelity field is covered deterministically; the pasted-image UI
  case was not repeated after that wording-only template hardening.
