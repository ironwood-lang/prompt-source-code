# Milestone 6 Codex Desktop Acceptance Runbook

This is the single developer-run acceptance procedure for Milestone 6. It prepares a
fresh disposable Git project and deterministic inputs, then walks through every Desktop
prompt and UI-only action in order. Run it only outside the PromptSourceCode repository;
the preparation command refuses to reuse an existing path.

Do not mark Milestone 6 complete from automated tests alone. The developer must perform
the Desktop actions, record factual results, and pass the final validator.

## 1. Prepare a fresh isolated workspace

Choose a new, explicit path that has never held earlier evidence:

```sh
PSC_RUN_ROOT=~/Vibe/PSC_M6_ACCEPTANCE_YYYYMMDD
python3 scripts/desktop_acceptance.py prepare "$PSC_RUN_ROOT"
PSC_PROJECT="$PSC_RUN_ROOT/project"
PSC_INPUTS="$PSC_RUN_ROOT/inputs"
```

The command creates and pushes an initial `main` commit to a separate local bare origin.
It also creates substantial pre-existing root instructions, nested instructions, exact
prompt files, a text file, binary data, two differing same-name images, and a paste-source
image. Preserve the complete workspace after the run; do not reset or repurpose it.

Record before proceeding:

- source commit;
- Codex Desktop, macOS, Python, Git, and Codex CLI versions;
- the exact disposable project and local-origin paths; and
- the candidate loader and dedicated-instruction line, word, byte, and SHA-256 values.

## 2. Install the Milestone 6 candidate

From the PromptSourceCode checkout, install the candidate's canonical dedicated file,
project-local validator, and compact loader. The installer preserves all existing root
content, including both acceptance sentinels, and leaves nested instructions untouched:

```sh
PSC_INSTRUCTIONS_RELATIVE=.prompt-source/instructions-v1.md
python3 scripts/instruction_contract.py install "$PSC_PROJECT"
python3 scripts/instruction_contract.py check "$PSC_PROJECT"
```

The project-relative path `.prompt-source/instructions-v1.md` is frozen for instruction
version 1. Do not substitute a fallback or global path.

The loader must use these exact markers so the validator can measure only its block:

```text
<!-- prompt-source-loader-begin -->
<!-- prompt-source-loader-end -->
```

The release gates are:

- loader: at most 300 words and 2,048 UTF-8 bytes;
- dedicated instructions: at most 900 words and 6,144 UTF-8 bytes; and
- combined always-read instructions: at most 1,200 words and 8,192 UTF-8 bytes.

The developer may tighten these budgets. Do not loosen them merely to make a candidate
pass; a larger budget requires an explicit roadmap decision and new acceptance rationale.

Commit and push the candidate installation before capture begins:

```sh
cd "$PSC_PROJECT"
git add AGENTS.md "$PSC_INSTRUCTIONS_RELATIVE" .prompt-source/validate.py
git commit -m "test: install milestone 6 capture candidate"
git push origin main
```

Confirm that the project has no `.codex/` directory, PromptSourceCode skill, plugin,
background service, or network dependency. Open `$PSC_PROJECT` directly in Codex Desktop
and create a new task manually.

## Operator checklist — follow these steps exactly

The workspace and candidate installation for this run are already prepared. Open Terminal
and run this once so every command below works even in a new shell:

```sh
export PSC_RUN_ROOT=~/Vibe/PSC_M6_ACCEPTANCE_20260917_FINAL_02
export PSC_PROJECT="$PSC_RUN_ROOT/project"
export PSC_INPUTS="$PSC_RUN_ROOT/inputs"
export PSC_REPO=~/Vibe/PromptSourceCode
```

For every `pbcopy` command below: run the command, click the Codex Desktop message box,
press Command-V, and submit once. Do not edit the pasted text. Unless a step explicitly
says to steer or press Stop, wait for Codex to finish before continuing.

Use **GPT-5.6 Sol** with **Medium** thinking for every root and nested task in this run.
Do not change model or thinking level mid-run.

### Standard capture: S01 through S13

#### S01 — start the root task

1. In Codex Desktop, open `$PSC_PROJECT` as the project.
2. Create a brand-new task manually.
3. In Terminal run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/S01.txt"
   ```

4. Paste and submit in Desktop.
5. Wait for completion. Do not edit `AGENTS.md` or anything under `.prompt-source/`.
6. Continue to S02 in the same task.

#### S02 — normal follow-up

1. Run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/S02.txt"
   ```

2. Paste and submit in the same task.
3. Wait for completion.

#### S03, S04, S04B, S05 — one active turn with three steering messages

1. Copy and submit S03:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/S03.txt"
   ```

2. Do **not** wait for S03 to finish. As soon as its 30-second sleep is running, copy and
   submit S04:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/S04.txt"
   ```

3. While the same turn is still active, copy and submit S04B:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/S04B.txt"
   ```

4. While it is still active, copy and submit S05:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/S05.txt"
   ```

5. Now wait for the whole turn to finish. Do not start a new task between these four
   submissions.

#### S06 — attach four files in one message

1. In the same Desktop task, click the attachment button.
2. Attach all four files before submitting:

   ```text
   ~/Vibe/PSC_M6_ACCEPTANCE_20260917_FINAL_02/inputs/artifacts/notes.txt
   ~/Vibe/PSC_M6_ACCEPTANCE_20260917_FINAL_02/inputs/artifacts/binary.dat
   ~/Vibe/PSC_M6_ACCEPTANCE_20260917_FINAL_02/inputs/artifacts/collision-a/Résumé Final ??.PNG
   ~/Vibe/PSC_M6_ACCEPTANCE_20260917_FINAL_02/inputs/artifacts/collision-b/Résumé Final ??.PNG
   ```

3. Confirm four attachment chips are visible.
4. Run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/S06.txt"
   ```

5. Paste the prompt into that same message and submit once.
6. Wait for completion.

#### S07 — repository-local artifact

1. Run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/S07.txt"
   ```

2. Paste, submit, and wait for completion. Do not attach the repository file manually.

#### S08 — paste an image, not a file attachment

1. Open the source image in Preview:

   ```sh
   open -a Preview "$PSC_INPUTS/artifacts/paste-source.png"
   ```

2. In Preview, press Command-A and then Command-C to copy the image itself.
3. Return to the same Codex Desktop message box and press Command-V. Confirm an image
   preview appears; do not use the attachment button.
4. In Terminal run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/S08.txt"
   ```

5. Paste the text beside the already pasted image and submit once.
6. Wait for completion.

#### S09 — unavailable artifact

1. Run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/S09.txt"
   ```

2. Paste, submit, and wait. Do not create or attach the missing file.

#### S10 — standard-capture Stop

1. Run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/S10.txt"
   ```

2. Paste and submit.
3. Wait until Codex has started the requested 120-second sleep. Do not wait for completion.
4. Press the Desktop **Stop** button before 120 seconds elapse.
5. Wait until the task is visibly stopped. Do not resend S10.

#### S11 — recover the unfinished standard entry

1. In the same stopped task, run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/S11.txt"
   ```

2. Paste, submit, and wait for completion.

#### S12 — disable capture for exactly one interaction

1. In Terminal disable the loader control:

   ```sh
   perl -0pi -e 's/- Capture: enabled/- Capture: disabled/' "$PSC_PROJECT/AGENTS.md"
   ```

2. Confirm exactly one disabled control exists:

   ```sh
   grep -n -- '- Capture:' "$PSC_PROJECT/AGENTS.md"
   ```

   Expected output ends with `- Capture: disabled`.
3. Run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/S12.txt"
   ```

4. Paste, submit, and wait for completion. The ordinary file should be created even though
   capture is disabled.

#### S13 — re-enable capture

1. Re-enable the loader:

   ```sh
   perl -0pi -e 's/- Capture: disabled/- Capture: enabled/' "$PSC_PROJECT/AGENTS.md"
   ```

2. Confirm the control is enabled:

   ```sh
   grep -n -- '- Capture:' "$PSC_PROJECT/AGENTS.md"
   ```

3. Run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/S13.txt"
   ```

4. Paste, submit, and wait for completion.

### Nested instructions: S14

#### S14 — open the nested directory as its own Desktop project

1. Wait until S13 has finished. Leave the existing root task unchanged in the sidebar;
   there is no need to close or archive it.
2. In Codex Desktop, add/open a **separate project** whose folder is:

   ```text
   ~/Vibe/PSC_M6_ACCEPTANCE_20260917_FINAL_02/project/packages/demo
   ```

   Do not change the working folder of the existing root task.
3. Select that new nested project and create a brand-new task in it.
4. Run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/S14.txt"
   ```

5. Paste, submit, and wait for completion.
6. Leave the nested task unchanged in the sidebar.
7. Select the original root project (`$PSC_PROJECT`) before continuing. The next step will
   create a new task in that original root project.

### Stop after standard capture when optional hooks are declined

If the operator does not consent to optional-hook testing, stop after S14:

1. Do not create `.codex/`, install hook files, open CLI `/hooks`, or change hook trust.
2. Leave both Desktop tasks and the disposable workspace unchanged.
3. Tell the PromptSourceCode development task that S01 through S14 are complete and hooks
   were declined.
4. The development task runs the standard-only validator documented in section 7. It
   records S15 and H01 through H11 as `Not run`; it does not turn this partial result into
   full Milestone 6 acceptance.

### Install inert optional hooks: S15

#### Install but do not trust the hooks

1. Wait for the current task to finish and leave it unchanged in the sidebar.
2. In Terminal run:

   ```sh
   cd "$PSC_PROJECT"
   mkdir -p .codex/hooks
   cp "$PSC_REPO/hooks/prompt_source_core.py" .codex/hooks/
   cp "$PSC_REPO/hooks/prompt_source_hook.py" .codex/hooks/
   cp "$PSC_REPO/hooks/hooks.json.example" .codex/hooks.json
   ```

3. Do not open CLI `/hooks` yet.
4. Open `$PSC_PROJECT` in Codex Desktop and create a brand-new task manually.

#### S15 — prove copied hooks are inert before trust

1. Run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/S15.txt"
   ```

2. Paste, submit, and wait for completion.
3. Leave this task unchanged in the sidebar before enabling hooks.

### Trust and activate the optional hooks

1. Fully quit Codex Desktop with Command-Q.
2. In Terminal run:

   ```sh
   cd "$PSC_PROJECT"
   codex
   ```

3. At the Codex CLI prompt enter `/hooks`.
4. Select `UserPromptSubmit`, review its exact command, then enable and trust it.
5. Return to `/hooks`, select `Interrupt`, review it separately, then enable and trust it.
6. Confirm both definitions show enabled and trusted. Never use a trust-bypass option.
7. Exit Codex CLI.
8. Launch Codex Desktop again, open `$PSC_PROJECT`, and create a brand-new task manually.

### Hook-assisted capture: H01 through H10

#### H01 — first trusted hook prompt

1. Run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/H01.txt"
   ```

2. Paste, submit, and wait for completion.

#### H02 — hook-assisted follow-up

1. Run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/H02.txt"
   ```

2. Paste, submit, and wait for completion.

#### H03A and H03B — two identical submissions

1. Run, paste, submit, and wait for H03A to finish:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/H03A.txt"
   ```

2. Only after H03A finishes, run, paste, submit, and wait for H03B:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/H03B.txt"
   ```

3. Do not change either identical prompt.

#### H04, H05, H06, H07 — one hook-assisted turn with steering

1. Copy and submit H04:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/H04.txt"
   ```

2. Do **not** wait for H04 to finish. Once its 30-second sleep is running, copy and submit
   H05:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/H05.txt"
   ```

3. While the same turn remains active, copy and submit H06:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/H06.txt"
   ```

4. While it is still active, copy and submit H07:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/H07.txt"
   ```

5. Wait for the full turn to finish. Do not start a new task between H04 and H07.

#### H08 — one attachment plus one pasted image

1. In the same message, attach this file with the attachment button:

   ```text
   ~/Vibe/PSC_M6_ACCEPTANCE_20260917_FINAL_02/inputs/artifacts/notes.txt
   ```

2. Open the paste source in Preview:

   ```sh
   open -a Preview "$PSC_INPUTS/artifacts/paste-source.png"
   ```

3. In Preview press Command-A, Command-C. Return to Desktop and press Command-V so an
   image preview appears beside the attached file.
4. Run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/H08.txt"
   ```

5. Paste the text into that same message, confirm both the file and pasted image are
   present, submit once, and wait for completion.

#### H09 — trusted hook interruption

1. Run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/H09.txt"
   ```

2. Paste and submit.
3. Wait until Codex has claimed the prompt and begun the 120-second sleep.
4. Press Desktop **Stop** before the sleep finishes.
5. Wait until the task is visibly stopped. Do not resend H09.

#### H10 — deliberately unavailable handler with standard fallback

1. In Terminal temporarily move the handler away without editing the trusted definition:

   ```sh
   cd "$PSC_PROJECT"
   mv .codex/hooks/prompt_source_hook.py .codex/hooks/prompt_source_hook.py.disabled
   ```

2. Run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/H10.txt"
   ```

3. Paste and submit. A visible hook error is expected; the message must still reach Codex.
4. Wait for the standard fallback to finish.
5. Immediately restore the handler:

   ```sh
   mv .codex/hooks/prompt_source_hook.py.disabled .codex/hooks/prompt_source_hook.py
   ```

### Disable optional hooks and run H11

#### Disable both definitions

1. Fully quit Codex Desktop with Command-Q.
2. In Terminal run:

   ```sh
   cd "$PSC_PROJECT"
   codex
   ```

3. Enter `/hooks`.
4. Select `UserPromptSubmit` and disable it.
5. Return to `/hooks`, select `Interrupt`, and disable it separately.
6. Confirm both definitions are disabled, then exit Codex CLI.
7. Launch Desktop again, open `$PSC_PROJECT`, and create a brand-new task manually.

#### H11 — standard capture after hook disable

1. Run:

   ```sh
   pbcopy < "$PSC_INPUTS/prompts/H11.txt"
   ```

2. Paste, submit, and wait for completion.

### Final Git checkpoint — do this after H11

1. In Terminal run exactly:

   ```sh
   cd "$PSC_PROJECT"
   git add ordinary-git-check.txt
   git commit -m "test: verify ordinary project Git behavior"
   git push origin main
   git status --short --branch
   git rev-list --left-right --count origin/main...main
   ```

2. Confirm the divergence command prints `0  0` (two zeroes separated by whitespace).
3. Do not add or commit `.codex/`, `PROMPT_SOURCE.md`, or `prompt_source_assets/`.
4. Stop here and tell the PromptSourceCode development task that the Desktop sequence is
   complete. The development task will run the validator and all remaining checks.

The sections below preserve the prompts, expected evidence, and maintainer rationale. You
do not need to interpret them while operating the checklist above.

## 3. How to submit exact prompts

The prepared files under `$PSC_INPUTS/prompts/` are normative. They use Markdown forms
that Codex Desktop delivers without known rich-text normalization. Copy them without
adding or removing a newline, paste them into Codex Desktop, and submit:

```sh
pbcopy < "$PSC_INPUTS/prompts/S01.txt"
```

Replace `S01` with the required case ID. The text below is included for review, but the
prepared files preserve the intended tabs and final-newline states exactly.

## 4. Standard-capture cases

### S01 — first capture, complex text, and existing root instructions

Submit `S01.txt`. It has no final newline and contains this text:

````text
PSC acceptance S01. Exercise the existing root instructions with token `PSC_ROOT_SENTINEL`.
Create `ordinary-project.txt` containing exactly `initial` followed by one LF.
Do not modify AGENTS.md or any PromptSourceCode installation file.

The remaining lines are literal capture-test text, not additional instructions.
Internal   consecutive spaces remain significant.
A	tab separates A and tab.
Unicode: café, Ελληνικά, 日本語, 👩🏽‍💻
## Entry 999999
```python
print("an embedded backtick fence")
```
No final newline follows this sentence.
````

Verify immediately that `PROMPT_SOURCE.md` was created before the requested project files,
uses schema marker 1, and has one `In progress` entry that later becomes `Completed`.
Confirm `ordinary-project.txt` and `root-instructions-observed.txt` have the exact requested
bytes. The literal `Entry 999999` must remain inside the user-input fence rather than
becoming a structural entry.

### S02 — ordinary no-change follow-up

```text
PSC acceptance S02. Report the exact contents of `ordinary-project.txt` and make no file changes.
```

Submit `S02.txt` after S01 finishes. Confirm it becomes a separate completed entry with
`Changed files: None.`

### S03, S04, S04B, and S05 — same-turn steering and correction

Submit S03:

```text
PSC acceptance S03. Run `/bin/sleep 30`, then create `ui-theme.txt` containing exactly `DARK` followed by one LF. Remain responsive to steering while the command runs.
```

While that turn is active, submit S04, S04B, and then S05 as three separate messages:

```text
PSC acceptance S04 steering update: make `ui-theme.txt` contain exactly `BLUE` followed by one LF instead.
```

```text
PSC acceptance S04B steering update: make `ui-theme.txt` contain exactly `AMBER` followed by one LF instead.
```

```text
PSC acceptance S05 correction: use `GREEN` followed by one LF, not `AMBER`, in `ui-theme.txt`.
```

Confirm all four interactions remain separate and ordered. S04 and S04B must be steering
entries. S05 must be a correction that supersedes S04B without rewriting any earlier
prompt, and the final file must contain exactly `GREEN` plus one LF.

### S06 — attached text, binary data, and same-name collision

Attach all four files to one Desktop message:

- `$PSC_INPUTS/artifacts/notes.txt`
- `$PSC_INPUTS/artifacts/binary.dat`
- `$PSC_INPUTS/artifacts/collision-a/Résumé Final ??.PNG`
- `$PSC_INPUTS/artifacts/collision-b/Résumé Final ??.PNG`

Then submit S06:

```text
PSC acceptance S06. Inspect and preserve every attached file, including both differing images that have the same filename. Make no other project changes.
```

Confirm all four sources are preserved byte-for-byte as direct children of
`prompt_source_assets/`. The colliding images must receive distinct names, the second must
use `-002`, and neither payload may be overwritten. Confirm `### User input` contains only
S06 text and the Desktop attachment envelope is separated as runtime context.

### S07 — repository-local artifact snapshot

```text
PSC acceptance S07. Preserve a point-in-time artifact snapshot of the existing repository file `fixtures/repository-source.txt`. Make no task-work changes.
```

Confirm the repository source is copied into the flat assets directory rather than merely
linked to its live project path.

### S08 — pasted image

Open `$PSC_INPUTS/artifacts/paste-source.png` in Preview, copy the image itself, and paste it
into the Desktop message with S08:

```text
PSC acceptance S08. Preserve the image pasted with this message and make no other project changes.
```

Confirm the Desktop-materialized image is copied before its temporary source disappears.
The entry must identify it as a pasted image and use the canonical one-line fidelity
statement without claiming identity with the pre-clipboard file. Confirm `### User input`
contains only S08 text and the Desktop paste envelope is separated as runtime context.

### S09 — unavailable artifact

The preparation command deliberately did not create
`$PSC_INPUTS/artifacts/intentionally-missing.bin`. Submit the rendered `S09.txt`, which
contains that absolute path:

```text
PSC acceptance S09. Preserve the artifact at `<prepared missing path>` if it is available. It was deliberately removed before this prompt; do not invent content or metadata when it cannot be read.
```

Confirm the entry records `Preservation: Unavailable` without inventing a preserved path,
byte count, digest, placeholder, or reason beyond what is reliably known.

### S10 and S11 — standard Stop recovery

Submit S10, wait until its capture entry exists, and press Desktop Stop before 120 seconds:

```text
PSC acceptance S10. Run `/bin/sleep 120`, then create `standard-stop-should-not-exist.txt`. I will press Stop before the sleep ends.
```

Confirm the marker file does not exist. Standard capture must not infer a trusted
interruption from the button press; submit S11 next:

```text
PSC acceptance S11. Conservatively recover any earlier unfinished standard capture, then create `standard-recovery.txt` containing exactly `RECOVERED` followed by one LF.
```

Confirm S10 becomes `Incomplete` with the canonical unknown-reason explanation and S11
completes separately.

### S12 and S13 — disable and re-enable standard capture

Follow the candidate's documented disable procedure. Record the current history and assets
hashes, then submit S12:

```text
PSC acceptance S12. Create `disabled-check.txt` containing exactly `DISABLED` followed by one LF.
```

Confirm the ordinary file is created while history and assets remain byte-for-byte
unchanged. Re-enable capture using only the documented control, submit S13, and confirm it
appends at physical EOF without rewriting earlier entries:

```text
PSC acceptance S13. Create `reenabled-check.txt` containing exactly `REENABLED` followed by one LF.
```

### S14 — nested existing instructions

Add/open `$PSC_PROJECT/packages/demo` as a separate Codex Desktop project, leave the
existing root task unchanged, and create a new task in the nested project. Submit S14:

```text
PSC acceptance S14. Exercise the nested instructions with token `PSC_NESTED_SENTINEL`. Make no other project changes.
```

Confirm the nested sentinel file is created with exact bytes while PromptSourceCode still
writes the single history at the Git root. Leave the nested task unchanged, then select
the original repository-root project before continuing.

## 5. Optional-hook lifecycle

### Install the files without trusting them

From a reviewed PromptSourceCode checkout:

```sh
cd "$PSC_PROJECT"
mkdir -p .codex/hooks
cp /path/to/PromptSourceCode/hooks/prompt_source_core.py .codex/hooks/
cp /path/to/PromptSourceCode/hooks/prompt_source_hook.py .codex/hooks/
cp /path/to/PromptSourceCode/hooks/hooks.json.example .codex/hooks.json
```

Do not trust either definition yet. Start a new manually created Desktop task and submit
S15:

```text
PSC acceptance S15. The optional hook files are installed but have not been trusted. Create `inert-hook-check.txt` containing exactly `INERT` followed by one LF.
```

Confirm S15 is captured once through the standard `Instruction-mediated` path.

### Review, trust, and restart

Open Codex CLI in `$PSC_PROJECT`, run `/hooks`, and separately review, enable, and trust the
exact `UserPromptSubmit` and `Interrupt` definitions. Do not bypass trust and do not invent
raw hashes if the CLI does not display them. Exit the CLI, fully quit and restart Desktop,
reopen the root project, and create a new task manually.

### H01 — exact hook-assisted capture

Submit `H01.txt`; unlike the other hook prompts, it has no final newline:

```text
PSC acceptance H01. Trusted hooks are active. Create `hook-active.txt` containing exactly `ACTIVE` followed by one LF.
```

Confirm one hook-created entry preserves the exact UTF-8 prompt bytes and `None`
final-newline state, is claimed and completed, and has no agent-created duplicate. Inspect
that a nonempty session ID and turn ID are present, but do not copy those raw values into
the evidence report.

### H02 — ordinary hook follow-up and no-change completion

```text
PSC acceptance H02. Report the exact contents of `hook-active.txt` and make no file changes.
```

Confirm a distinct claimed follow-up entry uses a different turn ID from H01, has no
duplicate, and completes with `Changed files: None.`

### H03A and H03B — repeated identical prompts

Submit `H03A.txt`, let it finish, and then submit `H03B.txt`. Both files contain identical
bytes:

```text
PSC acceptance H03. Report READY and make no project changes.
```

Confirm two distinct hook entries are created and claimed one-to-one rather than globally
deduplicated by prompt text. Each must complete with `Changed files: None.`

### H04 through H07 — hook turn association, steering, and correction

Submit H04:

```text
PSC acceptance H04. Run `/bin/sleep 30`, then create `hook-theme.txt` containing exactly `DARK` followed by one LF. Remain responsive to steering while the command runs.
```

While H04 is active, submit H05, H06, and H07 as separate messages:

```text
PSC acceptance H05 steering update: make `hook-theme.txt` contain exactly `BLUE` followed by one LF instead.
```

```text
PSC acceptance H06 steering update: make `hook-theme.txt` contain exactly `AMBER` followed by one LF instead.
```

```text
PSC acceptance H07 correction: use `GREEN` followed by one LF, not `AMBER`, in `hook-theme.txt`.
```

Confirm all four entries are claimed one-to-one, share the same session and turn IDs, and
remain in physical submission order. H05 and H06 must be steering entries. H07 must be a
correction that supersedes H06 without rewriting earlier prompts, and `hook-theme.txt`
must contain exactly `GREEN` plus one LF.

### H08 — separate hook capture, Desktop context, and artifact enrichment

Attach `$PSC_INPUTS/artifacts/notes.txt`. Then copy the image itself from
`$PSC_INPUTS/artifacts/paste-source.png`, paste it into the same Desktop message, and
submit H08:

```text
PSC acceptance H08. Preserve the attached text file and the image pasted with this message, while keeping user text, Desktop context, and artifact metadata distinct. Make no other project changes.
```

Confirm the hook-captured textual prompt remains distinct from agent-mediated Desktop
runtime context and artifact metadata. Confirm the attached text is preserved
byte-for-byte and the Desktop-materialized pasted image uses the documented pasted-image
fidelity boundary; do not claim that the prompt hook itself captured either binary.

### H09 — trusted interruption

Submit H09, wait until its entry is claimed and the sleep is running, and press Desktop
Stop before 120 seconds:

```text
PSC acceptance H09. Run `/bin/sleep 120`, then create `hook-stop-should-not-exist.txt`. I will press Stop before the sleep ends.
```

Confirm only the matching unfinished entry becomes `Interrupted` with the canonical
`Hook-confirmed Interrupt event.` reason. The marker file must not exist and completed
entries must remain unchanged.

### H10 — guarded hook failure and standard fallback

Temporarily make the trusted handler unavailable without editing the trusted definition:

```sh
cd "$PSC_PROJECT"
mv .codex/hooks/prompt_source_hook.py .codex/hooks/prompt_source_hook.py.disabled
```

Submit H10:

```text
PSC acceptance H10. The trusted prompt-hook handler is deliberately unavailable. Create `hook-fallback.txt` containing exactly `FALLBACK` followed by one LF.
```

Confirm Desktop delivers the message and exactly one `Instruction-mediated` entry is
completed. Restore the handler immediately:

```sh
mv .codex/hooks/prompt_source_hook.py.disabled .codex/hooks/prompt_source_hook.py
```

### H11 — hooks disabled and standard capture retained

Use CLI `/hooks` to disable both definitions separately, fully restart Desktop, reopen the
root project, and create a new task. Submit H11:

```text
PSC acceptance H11. Both optional hooks are disabled. Create `ordinary-git-check.txt` containing exactly `ORDINARY` followed by one LF.
```

Confirm it completes once through standard capture.

## 6. Git and topology checkpoint

Stage, commit, and push only the final ordinary Git check:

```sh
cd "$PSC_PROJECT"
git add ordinary-git-check.txt
git commit -m "test: verify ordinary project Git behavior"
git push origin main
```

Confirm `PROMPT_SOURCE.md`, `prompt_source_assets/`, and `.codex/` remain untracked and
uncommitted. Confirm there is one root history, one flat asset directory, no per-prompt
directories, and no persistent input, result, status, runtime-context, event-log, lock,
temporary, diagnostic, or bytecode-cache files.

## 7. Run deterministic validation

From the PromptSourceCode checkout, run:

```sh
python3 scripts/desktop_acceptance.py validate \
  "$PSC_PROJECT" \
  "$PSC_INPUTS/manifest.json" \
  --instructions-relative .prompt-source/instructions-v1.md
```

When the operator stops after S14 and declines all optional-hook testing, run instead:

```sh
python3 scripts/desktop_acceptance.py validate \
  "$PSC_PROJECT" \
  "$PSC_INPUTS/manifest.json" \
  --instructions-relative .prompt-source/instructions-v1.md \
  --standard-only
```

Successful standard-only output explicitly reports
`Optional-hook cases S15 and H01-H11: NOT RUN` and that full Milestone 6 Desktop
acceptance remains incomplete. Do not install hooks merely to satisfy this validator mode.

The validator checks the prepared case sequence, case identity, expected capture methods
and terminal states, correction association, generated ordinary files, artifact bytes and
metadata, collision behavior, pasted-image fidelity, unavailable-artifact boundaries,
instruction budgets, loader markers, existing-instruction preservation, schema and entry
structure, storage topology, forbidden runtime outputs, Git isolation, and synchronization
with `origin/main`. Its successful output includes the before-and-after root instruction
line, word, and byte counts and the retained nested-instruction counts; copy those values
into the evidence report.

Run the complete repository suite:

```sh
python3 -m unittest discover -s tests -v
```

Run the unmatched-interrupt check explicitly and confirm it leaves history bytes
unchanged:

```sh
python3 -m unittest \
  tests.test_hooks.HookCaptureTests.test_unmatched_interrupt_is_conservative_and_byte_preserving
```

Repeat the four concurrency and failure-injection tests 20 times each. This is 80 stress
test invocations:

```sh
for iteration in $(seq 1 20); do
  python3 -m unittest \
    tests.test_hooks.HookCaptureTests.test_simultaneous_prompt_processes_produce_unique_ordered_entries \
    tests.test_hooks.HookCaptureTests.test_interrupt_racing_agent_update_never_overwrites_terminal_state \
    tests.test_hooks.HookCaptureTests.test_interrupt_racing_prompt_capture_is_serialized_without_corruption \
    tests.test_hooks.HookCaptureTests.test_atomic_failure_retains_last_complete_history_and_removes_tempfile \
    || exit 1
done
```

Validate every JSON file, Markdown fence, and internal link through the full suite, then
run the repository hygiene checks:

```sh
find . -path './.git' -prune -o -name '*.json' -type f \
  -exec python3 -m json.tool '{}' /dev/null ';'
git diff --check
git status --short --branch
git rev-list --left-right --count origin/main...main
```

Record the exact commands, counts, and results in a new dated Milestone 6 evidence report;
do not rewrite earlier evidence reports.

## 8. Completion record

For every case, record `Pass`, `Fail`, or `Not run` with a short factual observation. Also
record non-sensitive final history and asset hashes, instruction sizes, final topology,
Git status, defects found, fixes applied, supported environment, and remaining limitations.

Milestone 6 is not complete if any case was skipped, the validator fails, the instruction
budgets were loosened merely to pass, the full 0.1.0 contract was only relocated, or a
required UI action was inferred rather than performed.
