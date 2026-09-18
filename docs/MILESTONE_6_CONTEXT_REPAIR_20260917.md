# Milestone 6 — S06/S08 context repair, 2026-09-17

## Preserved Desktop result

The operator completed S01–S14, including S04B, in
`~/Vibe/PSC_M6_ACCEPTANCE_20260917_FINAL_03`, reporting GPT-5.6 SOL Medium.
The installed candidate was `fc9af97991513687eca268f759bc3b107394891f`.
Complete Desktop task exports, actual file bytes, and the frozen-candidate acceptance
validator were checked. The root and separate nested task used the intended folders.

| Cases | Observed outcome |
| --- | --- |
| S01 | Pass: delivered text, root sentinel, ordinary file, and initial classification. |
| S02 | Pass: no task-work changes; reported the exact ordinary file contents. |
| S03, S04, S04B, S05 | Pass: separate chronological entries in one active Desktop turn; final GREEN value and backward correction reference. |
| S06 | Fail: all four attachments preserved exactly with correct kinds and collision names, but no separate runtime-context section. |
| S07 | Pass: repository snapshot preserved with correct classification and bytes. |
| S08 | Fail: Desktop-materialized pasted image preserved exactly with correct fidelity, but no separate runtime-context section. |
| S09 | Pass: missing requested source recorded as unavailable without invented bytes or digest. |
| S10, S11 | Pass: actual interrupted turn, no stop-target file, conservative incomplete status and successful recovery. |
| S12, S13 | Pass: capture disabled without provenance commands during S12, then resumed during S13. |
| S14 | Pass: separate nested project/task; initial classification, nested sentinel and root-only history. |
| S15, H01–H11 | Not run in this manual session. |

There were 14 captured entries, seven flat assets, and no installed hooks. No provenance
was tracked by Git. Two rejected helper invocations during S02/S04 were corrected within
the original task without extra entries or a remaining acceptance failure.

The original validator output remains:

```text
Desktop acceptance validation FAILED:
- S06 lacks separated Desktop runtime context
- S08 lacks separated Desktop runtime context
```

No captured entry, original artifact, installation file, Desktop export, or earlier
evidence report was repaired or replaced. Original evidence SHA-256 values:

- History: `56635bb24d6763a941821fbc8ccb4a870ec94dc547490c4cba62fc55f0b3092a`.
- Desktop export: `cfec34a5c6fc01563c1a70bb0a79d27017d064d518f68cab63932a0f03282917`.

## Cause and source repair

The contract required separated context, but the standard helper's artifact and result
operations did not assemble it. Both observed calls correctly reported Desktop artifact
kinds; the missing step was still left to manual model-generated Markdown.

`--preserve-artifact` now automatically inserts one fenced, path-free context summary for
observed `Attached file`, `Attached image`, and `Pasted image` records. It inserts before
artifacts, retains existing context, and handles unavailable sources without claiming
preservation. Filesystem-only snapshots do not acquire invented Desktop context.
Context and artifact metadata use one atomic history replacement under the existing lock.
New completions reject missing/empty context for Desktop artifacts. Hook enrichment
preserves existing context; hooks remain inert and optional.

The summary explicitly describes an agent-reported observation, not a verbatim Desktop
envelope or independent verification. User text, artifact facts, and the fidelity boundary
are unchanged. Historical schema-1 readers do not retroactively require this writer's
summary. The acceptance validator now parses a real, nonempty context payload and rejects
quoted headings, malformed/duplicate sections, and context placed after results.

## Deterministic replay, not a new Desktop UI run

Fresh baseline and fixed fixtures were prepared under
`~/Vibe/PSC_M6_CONTEXT_REPLAY_20260917_01`. The preparation script generated fresh project
guidance, inputs, manifest, and local Git origins. A read-only copy of the original first
six entries seeded each replay. Recorded S06/S07/S08 helper JSON was replayed through the
installed command-line helper, translating only fixture source paths. Recorded task
identity was simulated solely within the test subprocesses; no live task was created.
The pasted-image fixture used the actual Desktop-materialized bytes, not the pre-paste
source image.

The retained `replay.py` and `replay-result.json` contain the procedure and results:

- 106 assertions passed across the two variants.
- The old candidate reproduced the original history through S08 byte-for-byte, including
  both missing-context defects.
- The fixed candidate's only history differences were the S06 and S08 context insertions.
- S07 stayed byte-identical and had no invented context; all seven assets matched.
- The complete original acceptance evidence snapshot was unchanged after the replay.

This demonstrates the code-level repair using the actual failing helper requests. It is
not evidence that a fresh UI attachment/paste sequence ran with the revised candidate.

## Automated and repository checks

- Complete suite: 115 tests passed, including seven new regression tests and strengthened
  existing artifact, concurrency, failure-retention, and hook-enrichment checks.
- Explicit unmatched-interruption test: passed.
- Four required concurrency/failure tests repeated 20 times each: 80 invocations passed.
- Artifact-context concurrency and atomic-history-failure tests repeated 20 times each:
  40 additional invocations passed, for 120 stress invocations total.
- All four JSON fixtures and the hook JSON example parsed successfully; Markdown fences
  and internal links passed the full-suite check; `git diff --check` passed.
- No live history, assets directory, bytecode cache, persistent lock, or temporary capture
  output existed in the development repository. Hook assets remained inert and contained
  no network or Git operations; standard capture had no global configuration dependency.
- Changes stayed local on `milestone-6`; `main`, `origin/main`, and the inspected remote
  main remained `ef0cc942643e95b5405dc5ac72e30ae134718f53`. No GitHub push, tag, release,
  release-body edit, or published artifact was performed.

The first full-suite pass attempt caught a documentation phrase assertion after the
instruction sentence was reworded; wording was aligned and the complete suite rerun.
This was not a new Desktop failure.

Final enforced instruction measurements:

| Component | Words | UTF-8 bytes | Maximum words / bytes |
| --- | ---: | ---: | ---: |
| Marked loader | 196 | 1,523 | 300 / 2,048 |
| Dedicated instructions | 780 | 6,114 | 900 / 6,144 |
| Combined always-read contract | 976 | 7,637 | 1,200 / 8,192 |

The distribution manifest pins the revised instruction and helper assets. Their SHA-256
values are respectively
`6ce534674aa8bc5e3c4b3966e2a28791721210d648fc68a54e077b3084bf2a01` and
`f105c4cf6cda471b89b3e26c0a52a364bddadcef9c11c0017d7f82a196f83b6f`.

## Remaining acceptance boundary

S06/S08 are repaired and deterministically retested. A fresh Desktop confirmation of those
two cases on the revised candidate remains pending; this repair does not require the
operator to repeat S01–S14. Optional-hook cases also remain unperformed for this candidate.
Milestone 6 is therefore still in progress, not declared complete. Codex Desktop remains
the only supported capture environment.
