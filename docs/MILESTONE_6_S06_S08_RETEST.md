# S06 and S08 only — step-by-step retest

This run is complete. **Do not repeat these steps.** See the
[Desktop audit](MILESTONE_6_CONTEXT_RETEST_20260917.md) and
[automated reporting repair](MILESTONE_6_RESULT_REPAIR_20260918.md).
The instructions below are retained as the procedure used for that run.

The project was prepared with the fix from `b3cabfa` and no captured history.
**Run only the two messages below.** No hooks, steering, Stop test, or nested
project is needed. Leave all previous acceptance projects unchanged.

Every Terminal command below works from **any folder**, including in a new shell.
There are no environment variables to set up first.

## 1. Open the new project and start one task

1. In Codex Desktop, choose **Add project**. This is a separate project, not a change to
   an existing project's folder.
2. In the folder picker, press **Command-Shift-G**, paste this exact path, press Return,
   then choose Open:

   ```text
   ~/Vibe/PSC_M6_S06_S08_RETEST_20260917_01/project
   ```

   Select the final `project` folder, not its enclosing workspace. Click **Trust Folder**
   if asked.
3. Select that project and create **one brand-new task** in the local folder. Do not use
   a Git worktree or cloud environment.
4. Choose **GPT-5.6 SOL** and **Medium**, matching your previous run. Keep both unchanged.
5. Do not send a greeting, setup request, or trial message. S06 must be the first message.

## 2. S06 — attach four files, then submit one message

1. Add each file below to the same unsent message. For **each row**: click the attachment
   button, press **Command-Shift-G** in the picker, paste that row's path, press Return,
   and choose Open.

   | File | Exact path to paste |
   | --- | --- |
   | Text file | `~/Vibe/PSC_M6_S06_S08_RETEST_20260917_01/inputs/artifacts/notes.txt` |
   | Binary file | `~/Vibe/PSC_M6_S06_S08_RETEST_20260917_01/inputs/artifacts/binary.dat` |
   | First image | `~/Vibe/PSC_M6_S06_S08_RETEST_20260917_01/inputs/artifacts/collision-a/Résumé Final ??.PNG` |
   | Second image | `~/Vibe/PSC_M6_S06_S08_RETEST_20260917_01/inputs/artifacts/collision-b/Résumé Final ??.PNG` |

2. Confirm **four attachment chips** are visible. The two images intentionally have the
   same filename but different contents; include both. Do not submit yet.
3. In Terminal, copy the exact S06 prompt:

   ```sh
   pbcopy < "$HOME/Vibe/PSC_M6_S06_S08_RETEST_20260917_01/inputs/prompts/S06.txt"
   ```

4. Return to the same Desktop message box. Press **Command-V** to paste the text beside
   the four attachments. Do not edit the text.
5. Submit **once**, then wait until Codex finishes completely.
6. Stay in this same task. Do not run S07.

## 3. S08 — paste an image, then submit one message

1. In Terminal, open the image in Preview:

   ```sh
   open -a Preview "$HOME/Vibe/PSC_M6_S06_S08_RETEST_20260917_01/inputs/artifacts/paste-source.png"
   ```

2. In Preview, press **Command-A**, then **Command-C** to copy the image itself.
3. Return to the **same Codex Desktop task**. Click its empty message box and press
   **Command-V**. Confirm an image preview appears. **Do not use the attachment button**
   for this case, and do not submit yet.
4. Now copy the S08 text in Terminal:

   ```sh
   pbcopy < "$HOME/Vibe/PSC_M6_S06_S08_RETEST_20260917_01/inputs/prompts/S08.txt"
   ```

5. Return to the message box and press **Command-V** again. The message must contain the
   already-pasted image plus the S08 text. Do not edit the text.
6. Submit **once**, then wait until Codex finishes completely.

## 4. Stop and return here

Do not send another message in the test task, run another case, edit the history, or run
the full S01–S14 validator. Leave the task available; there is no need to close or archive
it. Return to the development conversation and say:

> S06 and S08 retest complete with GPT-5.6 SOL Medium.

I will retrieve the actual Desktop messages and check the two entries, separate runtime
context sections, all five preserved artifacts, exact bytes, and unchanged project
instructions. Because this is a fresh two-message task, S06 should be Entry 000001 / Initial
prompt and S08 Entry 000002 / Follow-up. Those are the correct expectations for this
focused retest, not the entry numbers from your full run.
