# Milestone 6 Artifact Repair — 2026-09-17

## Scope and status

The two artifact defects from the [focused preflight](MILESTONE_6_PREFLIGHT_20260917.md)
are repaired in local commit `fc9af97991513687eca268f759bc3b107394891f` on `milestone-6`.
The exact four-source failure is now an executable regression. Automated verification
passes. **The fresh live Desktop artifact retest is prepared but has not run at the time
of this report; the operator must add its project first.** No new manual S01–S14 run is
requested. Milestone 6 remains incomplete.

## Changes and boundaries

- `.prompt-source/validate.py --preserve-artifact` now owns copying, naming, verification,
  and artifact records. It uses the displayed entry number, including required padding.
- Filesystem source kind comes from the resolved path: inside the project means
  `Repository file snapshot`; outside means `Requested artifact`. The model cannot pass
  either of those kinds explicitly. Observed UI attachment/paste kinds remain agent input.
- Collision/reuse handling preserves both differing same-name images without overwrites.
  Missing/unreadable sources produce unavailable records without placeholder files.
- The writer appends artifact records before the result. `--finish-standard` rejects
  reserved capture sections inside a result string. This resolves the earlier assembly
  ambiguity without relabeling it as a proven historical schema failure.
- The parser rejects malformed padded prefixes. File validation now checks referenced
  copies against recorded sizes and hashes. Existing hook artifact facts cannot be
  replaced during later enrichment.

The loader path and markers, dedicated path, schema 1, and storage topology are unchanged.
No histories, artifacts, earlier reports, release bodies, tags, or published assets were
rewritten. Hook event handlers remain inert optional assets, with no network/Git code.
Standard capture needs no enabled hook or global configuration. Copies and history are
not a cross-file transaction; an interrupted publication can retain a complete unreferenced
asset for verified reuse. See [the helper contract](ARTIFACT_CAPTURE.md).

## Verification

- Full suite: **108 tests passed** on `/usr/bin/python3` 3.9.6 and Python 3.14.7.
- New artifact module: **17 tests**, including the exact P02 failure, repository/external
  and symlink classification, UI-kind/paste fidelity, naming edges, reuse across entries,
  missing/unreadable sources, terminal/foreign/disabled guards, copy/history failures,
  changed sources, tampered copies, hook enrichment, and concurrent preservation.
- Explicit unmatched-interruption test: **passed**.
- Four required concurrency/failure tests: **20 repetitions each, all passed**.
- Two existing standard-path race/failure tests and four new artifact race/failure tests:
  **20 repetitions each, all passed**. Total repeated checks: **200**.
- All five JSON/example-JSON files validated; all ten Python files parsed without caches.
- Markdown fence/internal-link tests and `git diff --check` passed; complete source and
  documentation diff inspected.
- No live history, assets, bytecode/cache directories, persistent runtime files, or
  installed hooks exist in the development repository. The document privacy scan passed.

The stronger file check initially exposed one incomplete automated fixture: the nested
validator regression installed the expected history without its referenced assets. The
test now materializes the existing byte-verified fixture payloads as well. This was not
the earlier `/var` versus `/private/var` path issue; resolved-path handling is unchanged.

Instruction sizes (whitespace-delimited words; UTF-8 bytes):

| Component | Actual | Maximum |
| --- | --- | --- |
| Bounded loader | 196 words / 1,523 bytes | 300 / 2,048 |
| Dedicated instructions | 778 words / 6,064 bytes | 900 / 6,144 |
| Combined | 974 words / 7,587 bytes | 1,200 / 8,192 |

The distribution loader file has one additional final LF outside the bounded block.
The distribution manifest was updated for the dedicated template and shared helper only;
the historical 0.1.0 release manifest is unchanged.

## Prepared focused retest

`scripts/desktop_acceptance.py prepare` created a new, previously nonexistent workspace:
`~/Vibe/PSC_M6_ARTIFACT_RETEST_20260917_01`. Its `project` subdirectory contains the candidate
installation, existing root/nested instructions, fixtures, and a local Git origin. The
complete prepared prompt/artifact manifest and `retest-plan.json` live outside the project.
No earlier evidence was reused or destroyed.

The planned request is identical to the failed four-file P02 request. In this new task it
will be Entry 000001, not Entry 000002. The audit will compare each source with its own
destination, check names/kinds/metadata and section layout, and inspect complete app-task
outputs. App-task dispatch is not UI-only acceptance; no attachment, paste, steering,
Stop, or optional-hook case will be credited by this retest.

The new project's installation was committed locally as `36b7ea8`; its `main` is
synchronized with its sibling bare origin. The old preflight history remains unchanged
at SHA-256 `c6e2592c5d93bd136d7a6a638605a9f67b92f724da5dfff452b5834d3d8d2ca6`.
Development `main`, `origin/main`, and the live remote main were verified at
`ef0cc942643e95b5405dc5ac72e30ae134718f53`. No development branch was pushed to GitHub.

## Files changed by the repair

New: `docs/ARTIFACT_CAPTURE.md`, `tests/test_artifact_capture.py`.

Updated: `hooks/prompt_source_core.py`, `templates/prompt-source-instructions-v1.md`,
`tests/fixtures/distribution-manifest.json`, `tests/test_format.py`,
`tests/test_instruction_contract.py`, `docs/INSTALLATION.md`, `docs/OPTIONAL_HOOKS.md`,
and `docs/TECHNICAL_REFERENCE.md`. This evidence report is a subsequent documentation
addition, not a change to an earlier report. No release artifact was published.
