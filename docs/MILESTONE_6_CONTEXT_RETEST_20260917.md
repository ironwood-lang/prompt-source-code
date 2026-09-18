# Milestone 6 — focused S06/S08 Desktop retest, 2026-09-17

## Scope and evidence

The operator repeated only S06 and S08 in the prepared fresh project
`~/Vibe/PSC_M6_S06_S08_RETEST_20260917_01/project`, reporting GPT-5.6 SOL Medium.
The candidate was `b3cabfac2781a9ae652b60669af3d73946d786f9`. This is actual
Desktop evidence, not the earlier deterministic replay. The model/thinking selection
is operator-reported, not independently attested by the task export.

The complete two-turn Desktop export and the 43 focused audit checks are retained as
`desktop-export.json` and `validation-result.json` beside the project, outside its
capture topology. Expectations were declared in `preparation.json` before execution;
that preparation snapshot and its full manifest were not rewritten after the run.
Audit completed at 2026-09-18 02:59 UTC (2026-09-17 local date).

Desktop task: `01a0b26b-a599-7612-be3f-b161b214cfcc`, titled
`Preserve attached files exactly`. Its complete export has exactly two user submissions
in separate completed turns. S06 finished before S08 began; both used the root project.

## Findings

The missing-runtime-context defects are resolved in both cases. Each entry has a real,
nonempty fenced context section before its artifact records, separate from user input.
The context is explicitly an agent-reported summary, not a verbatim Desktop envelope.

| Case | Verified capture outcome | Remaining result-reporting issue |
| --- | --- | --- |
| S06 | Entry 000001, Initial prompt, Completed; all four files preserved byte-for-byte, with correct kinds and distinct collision-safe image names. | Lists routine history/asset writes as task-work changed files. |
| S08 | Entry 000002, Follow-up, Completed, continues 000001; pasted image preserved byte-for-byte against the actual Desktop-materialized temporary file. | Lists routine history/asset writes as task-work changed files. |

Both captured prompts match their actual Desktop-delivered user text under the documented
`Unknown` final-newline boundary. Task identifiers match the export. There is no invented
hook turn ID or pasted-image original filename. The S08 fidelity statement correctly
does not claim identity with an unknown pre-clipboard source.

There is one remaining issue affecting both results: they list `PROMPT_SOURCE.md` and
captured assets under `Changed files`. These are routine provenance operations, not
task-work changes. Under [the result format](PROMPT_SOURCE_FORMAT.md#results-and-changed-files),
these cases should say `Changed files: None.`. Actual capture data is intact; this is
not a recurrence of the missing-context failure.

The installed `--validate-history` command passed with `history valid (2 entries)`.
The focused audit had **41 passing checks and two failing checks**, one result-reporting
check per case. Structural validation does not establish semantic result correctness.
The unmodified full-run validator was intentionally not used on this two-case project;
unperformed cases were not counted as passed.

One empty-stdin `--begin-standard` invocation in S06 was rejected and successfully retried
before task work. It left no extra entry and is not an unresolved capture defect.

## Storage, Git, and preservation

All five independent source/copy byte comparisons passed. There is exactly one root
history and five referenced assets in one flat directory. Baseline root and nested
instructions, the installed helper, and the repository fixture are byte-identical to
their prepared hashes. No hooks, extra runtime files, or ordinary project changes exist.

Generated provenance is untracked and unstaged. The test project's HEAD and local
`origin/main` remain `8b47e527ade09c5fcd7322f05af9b3891e91ed1c`; its origin is the
prepared sibling bare repository, not GitHub. The earlier full-run history and Desktop
export still match the hashes recorded before this retest.

New evidence SHA-256 values:

- History: `95298ccbdf53f5b5865527570a4e743de2d6b20e6953b3c257bb5cb0a04873a4`.
- Desktop export: `f21997d18ae0ff36852723bb7d95c473122144e5c3329e9b8ef772eacdfafb50`.

The development checkout remains on local `milestone-6` at the candidate commit.
Local `main` and `origin/main` remain `ef0cc942643e95b5405dc5ac72e30ae134718f53`;
this audit did not contact GitHub. No live provenance or bytecode caches were found in
the development repository. No implementation, test-project history, artifact,
installation, or earlier evidence report was changed. Only new audit evidence was added;
no commit, push, tag, or release was made.

## Acceptance boundary

The two context fixes now have fresh Desktop confirmation. Result reporting still needs
repair; no repair was made during this audit. Optional-hook cases remain unperformed on
this candidate, and this focused run does not establish complete Milestone 6 acceptance.
No additional manual run is requested by this report. Codex Desktop remains the only
supported capture environment.
