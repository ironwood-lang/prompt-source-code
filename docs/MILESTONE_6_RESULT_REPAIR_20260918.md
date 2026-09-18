# Milestone 6 — result-reporting repair, 2026-09-18

## Defect and repair

The [focused Desktop retest](MILESTONE_6_CONTEXT_RETEST_20260917.md) confirmed the S06/S08
runtime-context fixes, but both results incorrectly listed routine capture files as
task-work changes. All five artifacts were intact. The cause was a free-form completion
API: the helper accepted the model's entire result, including its changed-file report.

Standard completion now requires `entry_number`, a summary-only `result`, and a
`changed_files` array. The helper renders links or `Changed files: None.`, filters routine
root history/asset paths, and deduplicates normalized relative paths. Missing arrays,
unsafe paths, malformed flags, and legacy free-form changed-file reports fail before
writing. Mixed ordinary/provenance changes retain the ordinary paths; deleted paths and
Unicode filenames remain reportable. Explicit user-requested edits to provenance itself
can use `provenance_changes_requested: true`, without granting Git/publication authority.
Requests to preserve attachments are explicitly classified as routine capture.

The dedicated contract, its runtime digest, distribution manifest, format documentation,
and technical reference were aligned. The acceptance validator now checks the no-change
results of S06/S07/S08/S09 and H08 as well as the existing no-change cases. It inspects
the actual Result section, ignoring literal fenced examples, rather than accepting a
phrase anywhere in the entry. Historical schema-1 results remain readable and unchanged.

## Automated evidence

All commands used `PYTHONDONTWRITEBYTECODE=1`.

- `python3 -m unittest discover -s tests -v`: 127 tests passed (12 new tests).
- Explicit `test_unmatched_interrupt_is_conservative_and_byte_preserving`: passed.
- The four runbook concurrency/failure tests, each repeated 20 times: 80 passed.
- Artifact concurrency/history-failure tests, each repeated 20 times: 40 passed.
- New result-completion concurrency/atomic-failure tests, each repeated 20 times:
  40 passed. Total stress invocations: 160.
- All four JSON fixtures and the hook JSON example parsed; Markdown fences and internal
  links passed; `git diff --check` passed.
- Standard installed commands worked without hooks, including from nested directories.
  Optional hooks remained inert and free of network/Git operations; no global capture
  configuration dependency was introduced.

An initial full-suite run caught an overly strict acceptance check that counted a literal
fenced example following a valid no-change report as an error. The check was corrected
to inspect unfenced Result content, and the complete suite was rerun successfully.

## Replay of the actual failed completions

The existing Desktop project label `PSC_RETEST_01` resolves to
`~/Vibe/PSC_M6_S06_S08_RETEST_20260917_01/project`. No Desktop task was submitted, no new
Desktop project was added, and no trust action was required. That project was not updated.

The retained script and complete results are outside its capture directory, under
`~/Vibe/PSC_M6_S06_S08_RETEST_20260917_01/result-repair-replay-final-20260918/`.
Running `replay.py` with the development repository path creates isolated baseline/fixed
copies and refuses to overwrite existing replay directories. It reopens only copied
entries for simulated completion; no original history is reopened or rewritten.

All 34 replay checks passed. The old helper reproduced the entire observed history
byte-for-byte, including both reporting defects. The repaired helper rejected the original
malformed completion requests without changing pending bytes; resubmitting their factual
summaries and structured path arrays produced `Changed files: None.` in both entries.
Only their Result formatting differed: prompts, metadata, context, artifact records, and
all five asset byte sequences were unchanged. The actual Desktop project and export were
also unchanged. This is deterministic helper replay, not a new Desktop UI acceptance run.

## Instruction budgets and repository state

| Component | Words | UTF-8 bytes | Maximum words / bytes |
| --- | ---: | ---: | ---: |
| Loader | 196 | 1,523 | 300 / 2,048 |
| Dedicated instructions | 767 | 6,085 | 900 / 6,144 |
| Combined | 963 | 7,608 | 1,200 / 8,192 |

Architecture remains the marked root loader, canonical `.prompt-source/instructions-v1.md`,
and project-local `.prompt-source/validate.py`. The loader and storage schema did not change.
Updated copyable assets are the dedicated instructions and shared helper, pinned in
`tests/fixtures/distribution-manifest.json`. No release artifact, tag, or release body
was created or changed; README remains unchanged and end-user focused.

The implementation, acceptance checks, four existing test modules, new
`tests/test_result_capture.py`, and two contract documents changed. This repair commit also
retains the previously uncommitted focused run guide and factual audit report; neither
the original Desktop history nor an earlier evidence report was repaired.

No live history, assets directory, bytecode cache, or temporary capture output exists in
the development repository. Both prior Desktop histories/exports retain their recorded
hashes. Local `main`, `origin/main`, and the read-only remote main check all resolve to
`ef0cc942643e95b5405dc5ac72e30ae134718f53`. Work remains local on `milestone-6`; no push.

## Resume boundary

The result-reporting repair is implemented and automatically verified. No repeat of
S01–S14 is requested for it. The revised structured completion contract has not received
a fresh model-driven Desktop run; summary/path selection remains model-mediated.
Optional-hook Desktop acceptance remains unperformed on this candidate, so Milestone 6
is not declared complete. Codex Desktop remains the only supported capture environment.
Any future Desktop work should use the existing `PSC_RETEST_01` project if suitable,
preserving its original evidence before an installation update.
