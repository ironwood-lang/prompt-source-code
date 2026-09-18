# Focused Desktop retest: H07 and H08

This repeats only the two failed cases from FULL_01, with one prerequisite message so H07
can correct an earlier request in the same active turn. **Three submissions total:**
setup (H00), H07, H08. Do not repeat S01–S15 or the other H cases.

The [repair evidence report](MILESTONE_6_H07_H08_REPAIR_20260918.md) records the changes and
automated checks. This run is now complete: [H07 and H08 passed](MILESTONE_6_H07_H08_VALIDATION_20260918.md).
The steps below retain the procedure used; do not repeat this completed workspace.

The development task prepares a separate disposable workspace:
`~/Vibe/PSC_M6_H07_H08_RETEST_20260918_01`. Standard capture and exact prompt/image inputs
are already installed. The repaired files are frozen under its `candidate/` directory;
their hashes and the installation are recorded in `preparation.json`. At preparation,
optional hooks were not installed, enabled, or trusted, and no acceptance prompt had
been submitted. The linked validation report records the subsequent completed run.

Leave `PSC_M6_ACCEPTANCE_20260918_FULL_01`, all its evidence, and its five tasks unchanged.
This retest uses a new root project and one brand-new Local task. Use **GPT-5.6 SOL,
Medium** throughout. If unavailable, stop and report it here instead of choosing a substitute.

## 1. Initialize Terminal variables

Paste this complete block into Terminal. Repeat it if you open a new shell:

```sh
export PSC_H_RUN=~/Vibe/PSC_M6_H07_H08_RETEST_20260918_01
export PSC_H_PROJECT="$PSC_H_RUN/project"
export PSC_H_INPUTS="$PSC_H_RUN/inputs"
export PSC_H_FROZEN="$PSC_H_RUN/candidate"
```

Verify the prepared standard installation:

```sh
python3 -B "$PSC_H_FROZEN/scripts/instruction_contract.py" check "$PSC_H_PROJECT"
```

If the directory is missing or any command fails, stop and report the error to the
development task. Do not rerun preparation, repair history, or reuse FULL_01.

## 2. Review and install the frozen hooks

Review these three files in your editor:

```text
candidate/hooks/prompt_source_core.py
candidate/hooks/prompt_source_hook.py
candidate/hooks/hooks.json.example
```

Those paths are relative to `$PSC_H_RUN`. Copy only those frozen files into the new project:

```sh
cd "$PSC_H_PROJECT"
test ! -e .codex &&
  mkdir -p .codex/hooks &&
  cp "$PSC_H_FROZEN/hooks/prompt_source_core.py" .codex/hooks/ &&
  cp "$PSC_H_FROZEN/hooks/prompt_source_hook.py" .codex/hooks/ &&
  cp "$PSC_H_FROZEN/hooks/hooks.json.example" .codex/hooks.json
```

Copying the files does not grant trust. Do not send a test prompt yet.

## 3. Enable and trust both hooks, then restart Desktop

1. Fully quit Codex Desktop with Command-Q.
2. In Terminal run:

   ```sh
   cd "$PSC_H_PROJECT"
   codex
   ```

3. At the CLI prompt enter `/hooks`.
4. Select `UserPromptSubmit` from **this new project's** `.codex/hooks.json`. Review its
   exact command and source, then enable and trust it.
5. Return to `/hooks`, select this project's `Interrupt`, and review, enable, and trust
   it separately.
6. Confirm both definitions are enabled and trusted. Never bypass trust or edit managed
   trust data. If the definitions or controls differ, stop and report what you see.
7. Exit the CLI with Control-C, twice if requested. Wait for the normal Terminal prompt.
   Do not submit acceptance prompts through the CLI.
8. Launch Codex Desktop again.

The procedure follows the repository's existing
[optional-hook lifecycle](OPTIONAL_HOOKS.md#review-and-trust-each-definition).

## 4. Add the new root project and create one Local task

1. Copy the project directory:

   ```sh
   printf '%s' "$PSC_H_PROJECT" | pbcopy
   ```

2. In Desktop choose Add project. In the folder picker press Command-Shift-G,
   Command-V, Return, then Open. Trust the project folder if prompted; folder trust
   is separate from the hook trust reviewed above.
3. Select this project and create a brand-new **Local** task. Use the prepared folder
   directly, without a worktree or cloud environment.
4. Set **GPT-5.6 SOL, Medium** before submitting anything.
5. Do not send a greeting, setup explanation, or this guide to that task.

## 5. Run H07 with its prerequisite

1. Copy the prerequisite prompt:

   ```sh
   pbcopy < "$PSC_H_INPUTS/prompts/H00.txt"
   ```

2. Paste it into the new Desktop task and submit once. It requests a 120-second sleep
   followed by an AMBER file. The sleep provides time to send the correction.
3. Wait until the `/bin/sleep 120` command is visibly running. **Do not wait for the
   task to finish and do not press Stop.**
4. While that same turn is active, copy H07:

   ```sh
   pbcopy < "$PSC_H_INPUTS/prompts/H07.txt"
   ```

5. Paste and submit it in the same task immediately. H07 changes AMBER to GREEN.
6. Now wait for the whole turn to finish. Do not send another message.

If the prerequisite finishes before you submit H07, stop and report that in the
development task. Do not resend either prompt. The setup is a prerequisite, not a claim
that the full H04–H06 sequence was repeated.

## 6. Run H08 in the same task

1. After H07 has finished, print the attachment path:

   ```sh
   printf '%s\n' "$PSC_H_INPUTS/notes.txt"
   ```

2. In the same Desktop task, click the attachment button. Use Command-Shift-G in the
   picker, paste the printed path, press Return, and choose Open.
3. Open the image in Preview:

   ```sh
   open -a Preview "$PSC_H_INPUTS/paste-source.png"
   ```

4. In Preview press Command-A, then Command-C to copy the image itself.
5. Return to the Desktop message box and press Command-V. Confirm an image preview
   appears alongside the attached text file. Use a paste for the image, not the attachment button.
6. Copy H08's text:

   ```sh
   pbcopy < "$PSC_H_INPUTS/prompts/H08.txt"
   ```

7. Paste the text beside the attachment and image. Submit **once**, then wait for completion.

## 7. Disable the retest hooks

1. Fully quit Desktop with Command-Q.
2. Run `cd "$PSC_H_PROJECT"` and then `codex` in Terminal.
3. Enter `/hooks`; disable this project's `UserPromptSubmit` and `Interrupt` separately.
4. Confirm both are disabled, exit the CLI, and launch Desktop again.
5. Leave the retest task and every file unchanged. Do not submit H11 or any additional prompt.

## 8. Report completion here

Return to the PromptSourceCode development task and say:

> H07/H08 focused retest complete using GPT-5.6 SOL Medium.

Report any deviation, skipped action, or unexpected error. There is no manual Git check
in this focused run, and its disposable project has no remote. Do not commit or push its
generated history, assets, or hook files. The development task will retrieve the actual
Desktop evidence and run the focused validator; you do not need to audit the history.

## Maintainer preparation and validation

Preparation is performed once by the coordinator before the operator handoff:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/hook_retest.py prepare \
  ~/Vibe/PSC_M6_H07_H08_RETEST_20260918_01
```

The command refuses existing paths and development-repository destinations. It freezes
source files, installs standard capture, prepares three prompts and two inputs, and makes
one local installation commit in the disposable repository. It does not install project
hooks, grant trust, add a remote, submit prompts, or touch earlier workspaces.

After the operator reports completion, retrieve every page of the new Desktop task,
including all user-message items and complete command outputs. Save those actual pages
to `$PSC_H_RUN/desktop-export.json`. Check the task-specific execution record for the
requested model/effort and the dedicated-instruction read before work. Preserve a copy of
the Desktop-materialized H08 temporary image while available, outside `project/`.

Run the frozen focused validator:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B "$PSC_H_FROZEN/scripts/hook_retest.py" validate \
  "$PSC_H_RUN" --desktop-export "$PSC_H_RUN/desktop-export.json"
```

If the temporary image has disappeared but its actual bytes were already preserved,
pass that evidenced copy with `--pasted-source /path/to/preserved-desktop-image.png`.
Never substitute the pre-clipboard fixture for missing Desktop image evidence.

Require exactly three claimed, completed hook entries in one task: H00 initial, H07
correction superseding Entry 1 in the same turn, and H08 follow-up in a later turn. Check
exact Desktop-delivered user text, GREEN plus LF, no runtime paths in user input, a
separate runtime-context section, two source-identical correctly classified artifacts,
no-change H08 result, unchanged snapshot/installation, and Git/topology isolation.
Report failures before repair and preserve the complete validator output.

A pass confirms only these focused cases on the repaired snapshot. It does not rewrite
FULL_01's failed result, substitute synthetic evidence, or by itself declare full
Milestone 6 acceptance complete. Do not request another full manual run without a
demonstrated need.
