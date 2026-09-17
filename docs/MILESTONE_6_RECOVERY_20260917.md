# Milestone 6 Recovery Audit — 2026-09-17

## Status and evidence boundary

The recurring defects have code-level fixes and passing deterministic regressions.
Milestone 6 is **not complete**: the revised candidate has not completed live Desktop
acceptance, and S15/H01–H11 were not performed in this run. This report does not turn
synthetic tests or earlier-candidate observations into a new Desktop pass.

No additional full S01–S14 manual run is requested. The captured project at
`~/Vibe/PSC_M6_ACCEPTANCE_20260917_FINAL_02/project` remains unchanged. Earlier evidence reports,
including [the earlier validation report](MILESTONE_6_VALIDATION_20260917.md), are preserved
as historical records, not edited to match this implementation.

## Read-only audit of the completed Desktop run

The installed candidate matches source commit
`fbb298cbc9644ec610c6bd35dfb342d0a17b42df`. The reproducible command below uses its
verified local short reference `fbb298c`. No candidate files were updated in the evidence
project.

The root task was `01a0b148-1813-7123-9642-4a6fe7f42cd3`; the nested task was
`01a0b155-9a55-7190-985c-d2de5bc97b64`. The latter actually used the separate
`project/packages/demo` project. The operator's project choice was correct.

Three complete `read_thread` pages supplied the Desktop-delivered user messages and turn
states. Their evidence export is outside the captured project at
`~/Vibe/PSC_M6_ACCEPTANCE_20260917_FINAL_02/desktop-export-20260917-audit.json`.
It is not a capture-runtime file or dependency, and was not reconstructed from history.

| Case | Factual outcome in the preserved run |
| --- | --- |
| S01 | Delivered text and root-instruction output match. Desktop inserted blank lines; comparing against clipboard bytes was a validator false positive. |
| S02 | No-change follow-up and result pass. |
| S03 | Initial active-turn request retained as a separate completed entry. |
| S04 | First active-turn steering retained separately. |
| S04B | Second active-turn steering retained separately. |
| S05 | Explicit active-turn correction retained with its backward supersession reference. |
| S06 | Four attachments preserved; differing same-name images remain distinct. |
| S07 | Repository snapshot and verified bytes pass. |
| S08 | Pasted-image artifact and bounded fidelity statement pass. |
| S09 | Unavailable artifact recorded without invented copy metadata. |
| S10 | Desktop confirms an interrupted turn; history retains the conservative standard incomplete reason. |
| S11 | Recovery and requested ordinary output pass. |
| S12 | **Failed:** disabled capture still created Entry 000013. |
| S13 | Re-enabled capture and requested output pass; earlier text failure was caused by positional misalignment after S12. |
| S14 | **Failed:** a genuinely new nested task was recorded as `Follow-up`, not `Initial prompt`. Text and nested instruction output pass. |
| S15, H01–H11 | **Not run.** No hook acceptance claim. |

Reproduction from this repository, with no evidence mutation:

```sh
export PSC_RUN_ROOT=~/Vibe/PSC_M6_ACCEPTANCE_20260917_FINAL_02
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 scripts/desktop_acceptance.py validate \
  "$PSC_RUN_ROOT/project" "$PSC_RUN_ROOT/inputs/manifest.json" \
  --standard-only --candidate-ref fbb298c \
  --desktop-export "$PSC_RUN_ROOT/desktop-export-20260917-audit.json"
```

Complete validator error output (exit 1, correctly retained):

```text
Desktop acceptance validation FAILED:
- disabled case S12 was unexpectedly captured (Entry 000013)
- S14 has interaction 'Follow-up'
```

The original history remains 10,588 bytes, SHA-256
`6f807f3602d179e24b102dfad2e067f3153db55cf247d8dc8863445208389afb`.
All six existing flat assets retained their bytes and SHA-256 values during this audit.

## Defects and implemented fixes

1. **The disable switch depended on remembered instructions.** The loader now checks the
   live on-disk state on every submission. Entry creation and completion reread it under
   the directory lock; disabled capture performs no provenance writes. Invalid, missing,
   unreadable, stale, conflicting, or truncated instructions fail closed for capture.
2. **Task classification was left entirely to narrative interpretation.** Standard
   creation now requires explicit conversation context and uses the real runtime
   `CODEX_THREAD_ID` when present. A new task cannot silently use another task's history
   as evidence of a prior submission. No identifier is generated or guessed.
3. **The acceptance oracle conflated clipboard text with Desktop delivery.** Validation
   now compares against exported Desktop user messages, preserving internal whitespace.
   It permits only the declared unknown final-newline boundary, not arbitrary text
   normalization. Missing exports are missing evidence, not a pass or a capture failure.
4. **One extra entry caused cascading false failures.** Cases now match by their prepared
   labels, with separate ordered observations for deliberately repeated prompts. Missing,
   duplicate, out-of-order, and disabled captures remain failures without shifting later
   comparisons.
5. **Correction wording contradicted schema 1.** An explicit correction can occur during
   or after a turn. Other active-turn updates are steering; the revised contract follows
   the existing format rather than redefining it.
6. **Nested invocation remained fragile.** Installed helper commands derive the project
   root from the installed helper's location, including absolute invocations from a nested
   cwd. Path regression tests compare resolved paths; macOS `/var` and `/private/var`
   aliases do not represent different projects.

The standard helper now creates canonical headers, dynamic fences, sequence numbers, and
atomic text writes, and finalizes only the named unfinished standard entry. This reduces
the formatting decisions delegated to the model. Artifact/context enrichment and delivered
text selection still require model compliance; this is not deterministic capture of the UI.

## Architecture, budgets, and changed distribution assets

The canonical contract remains `.prompt-source/instructions-v1.md`, loaded by exactly one
bounded block in the root `AGENTS.md`. The exact markers remain
`<!-- prompt-source-loader-begin -->` and `<!-- prompt-source-loader-end -->`.
Existing root and nested instructions continue to apply. `.prompt-source/validate.py` is
project-local support code, not an enabled hook or an extra always-read instruction file.

| Instruction component | Words | UTF-8 bytes | Maximum words | Maximum bytes |
| --- | ---: | ---: | ---: | ---: |
| Bounded loader | 196 | 1,523 | 300 | 2,048 |
| Dedicated contract | 783 | 6,071 | 900 | 6,144 |
| Combined | 979 | 7,594 | 1,200 | 8,192 |

The loader distribution file includes one trailing LF outside the marked block: 1,524
bytes. Both measurement interpretations stay below the limits.

Changed distribution sources are the loader, dedicated contract, standard installer,
shared helper, and their current distribution manifest. The optional hook wrapper and
disabled hook definitions remain unchanged. No release body, tag, published release,
historical release manifest, or downloadable release artifact was modified or published.

Documentation updates cover installation, updating and refreshing tasks, disabling and
re-enabling capture in an existing task, nested-project selection, optional-hook controls,
delivered-text evidence, and historical-candidate replay. The README remains end-user
focused. Detailed implementation behavior is in [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md).

Files changed in this repair:

- `hooks/prompt_source_core.py`, `scripts/instruction_contract.py`,
  `scripts/desktop_acceptance.py`.
- `templates/AGENTS.prompt-source-loader.md`, `templates/prompt-source-instructions-v1.md`.
- `tests/test_standard_capture.py` (new), `tests/test_desktop_acceptance.py`,
  `tests/test_format.py`, `tests/test_instruction_contract.py`, `tests/fixtures/README.md`,
  `tests/fixtures/distribution-manifest.json`.
- `README.md`, `docs/COMPATIBILITY.md`, `docs/INSTALLATION.md`,
  `docs/MANUAL_CODEX_DESKTOP_VALIDATION.md`, `docs/MILESTONE_6_CODEX_DESKTOP_ACCEPTANCE.md`,
  `docs/OPTIONAL_HOOKS.md`, `docs/TECHNICAL_REFERENCE.md`, and this new evidence report.

## Automated verification

Environment: macOS 26.6.2 (25G83), system Python 3.9.6, development Python 3.14.7,
Git 2.54.0 (Apple Git-157). The supported capture environment remains Codex Desktop;
running Python checks does not add support for other agent environments.

- Complete suite: **91/91 passed independently on both Python versions**.
- Explicit unmatched-interruption test: **passed**.
- Four required concurrency/failure tests, 20 repetitions each: **80/80 passed on each
  Python version**.
- Two additional standard-helper concurrency/completion-failure tests, 20 repetitions
  each: **40/40 passed on each Python version**. Each concurrent test launches 12 separate
  helper processes, with no lost entry, duplicate number, or extra runtime file.
- All five repository JSON/JSON-example files parse; all nine Python files compile in
  memory without producing bytecode caches.
- Markdown fences, internal links, canonical paths/markers, word/byte budgets, and
  distribution hashes pass.
- Standard root/nested commands pass with no installed or enabled hooks. Existing hook
  tests still establish inert defaults and absence of network or Git operations.
- Full acceptance-validator fixtures distinguish real failures from the S01 whitespace
  and shifted-case false positives; these fixtures are explicitly synthetic, not UI runs.
- `git diff --check` passes. No live `PROMPT_SOURCE.md`, `prompt_source_assets/`, or
  bytecode caches exist in this development repository. Two preexisting ignored cache
  directories were moved to a recoverable temporary backup, not deleted.

The complete source, test, and documentation diff was reviewed. Work remains local on
`milestone-6`. `main`, `origin/main`, and the read-only remote main check all resolve to
`ef0cc942643e95b5405dc5ac72e30ae134718f53`. No push is authorized or performed.

## Remaining boundary

The code guards are tested; the model following the revised instructions has not been
validated in a new Desktop task during this repair. Focused live confirmation should
target disable/re-enable in one task and the first submission in a separate nested task,
without altering the old evidence or repeating unaffected cases. A focused check would
still not satisfy the complete Milestone 6 gate or the unperformed optional-hook cases.

No global Codex configuration, skill, plugin, background service, or network is required
for standard capture. Histories and assets keep schema 1 and the same two-location storage
topology. Existing evidence is preserved; remaining uncertainty is stated rather than
hidden behind a promise that a model-mediated path can never fail.
