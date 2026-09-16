<!-- prompt-source-schema: 1 -->

# Prompt Source

This file records the chronological user interactions that shaped this project. User
input is preserved at the Codex Desktop delivery boundary described by PromptSourceCode
format version 1.

Generated history and assets are local provenance. Do not stage, commit, push, publish,
or upload them unless the user explicitly requests it.

## Entry 000001

- Interaction: Initial prompt
- Status: Completed
- Capture method: Instruction-mediated

### User input

- Final newline: None

``````````text
  Pleese  keep   every space.   
	A tab starts this line	and one sits between words.

# This is user input, not a history heading

[a Markdown link](https://example.test/a_(b))
Unicode: café, Ελληνικά, 日本語, 👩🏽‍💻

`````````python
print("a nested backtick fence")
`````````

~~~~~~~~~~~text
and an unusually long tilde fence
~~~~~~~~~~~

## Entry 999999
### Result
- Status: Interrupted
<!-- prompt-source-schema: 999 -->
No final newline follows this sentence.
``````````

### Result

Preserved the complex instruction as a literal dynamically fenced payload.

Changed files: None.

## Entry 000002

- Interaction: Follow-up
- Status: Completed
- Capture method: Instruction-mediated
- Continues: Entry 000001

### User input

- Final newline: LF

```text
Now give me a short summary of what you preserved.
```

### Result

Summarized the preserved whitespace, Unicode, Markdown, and nested fences.

Changed files: None.

## Entry 000003

- Interaction: Steering
- Status: Completed
- Capture method: Instruction-mediated
- Continues: Entry 000002

### User input

- Final newline: LF

```text
Use blue for the example badge.
```

### Result

Recorded the color direction; Entry 000005 superseded it before implementation.

Changed files: None.

## Entry 000004

- Interaction: Steering
- Status: Completed
- Capture method: Instruction-mediated
- Continues: Entry 000002

### User input

- Final newline: LF

```text
Keep the label to three words.
```

### Result

Applied the three-word label constraint to the in-progress task.

Changed files:

- [src/badge.txt](<src/badge.txt>)

## Entry 000005

- Interaction: Correction
- Status: Completed
- Capture method: Instruction-mediated
- Supersedes: Entry 000003

### User input

- Final newline: LF

```text
Correction: make the badge amber, not blue.
```

### Result

Used amber and retained the earlier blue instruction unchanged in Entry 000003.

Changed files:

- [src/badge.txt](<src/badge.txt>)

## Entry 000006

- Interaction: Follow-up
- Status: Completed
- Capture method: Instruction-mediated
- Continues: Entry 000005

### User input

- Final newline: LF

```text
Review the attached notes and report their encoding.
```

### Codex Desktop runtime context

- Final newline: None
- Boundary note: Synthetic Desktop attachment envelope; not user-authored.

```text
Attached file: notes.txt
My request:
Review the attached notes and report their encoding.
```

### Artifacts

#### Artifact 1

- Kind: Attached file
- Original name (JSON): "notes.txt"
- Preserved copy: [prompt-000006-notes.txt](<prompt_source_assets/prompt-000006-notes.txt>)
- Byte count: 34
- SHA-256: 28c0632356506034aba615a14939b0631f2f3ea9cdc2bc99abb3e9ec468b6b2f
- Fidelity: Byte-for-byte copy of the attached original exposed by Codex Desktop.

### Result

Reported that the attached text fixture is UTF-8 and contains a final LF.

Changed files: None.

## Entry 000007

- Interaction: Follow-up
- Status: Completed
- Capture method: Instruction-mediated
- Continues: Entry 000006

### User input

- Final newline: LF

```text
Use the attached image as a one-pixel fixture.
```

### Artifacts

#### Artifact 1

- Kind: Attached image
- Original name (JSON): "Logo Final.PNG"
- Preserved copy: [prompt-000007-Logo-Final.png](<prompt_source_assets/prompt-000007-Logo-Final.png>)
- Byte count: 70
- SHA-256: afab3cd49cf0a47b361ed2b78bd43febfa7fcfd0ab49fc065d5c36c505a4da98
- Fidelity: Byte-for-byte copy of the attached original exposed by Codex Desktop.

### Result

Recorded the attached original as a byte-preserved image fixture.

Changed files: None.

## Entry 000008

- Interaction: Follow-up
- Status: Completed
- Capture method: Instruction-mediated
- Continues: Entry 000007

### User input

- Final newline: LF

```text
Use this pasted image too, but distinguish it from the original file.
```

### Codex Desktop runtime context

- Final newline: None
- Boundary note: Desktop supplied image context separately from the textual user input.

```text
Synthetic image envelope was present; no literal <image> tag was user-authored.
```

### Artifacts

#### Artifact 1

- Kind: Pasted image
- Original name (JSON): "image.png"
- Preserved copy: [prompt-000008-image-001.png](<prompt_source_assets/prompt-000008-image-001.png>)
- Byte count: 110
- SHA-256: e8f8b0ee40de543ed9937f65b2940765a3347d18c4cc92137369e0c7423a0eb3
- Fidelity: Byte-for-byte copy of the clipboard image materialized by Codex Desktop; binary identity with any pre-clipboard source is not claimed.
- Pre-clipboard comparison: Fixture pixels match, but the 70-byte source SHA-256 was 3759a41b8b57aa59c46ce086048042297abed9ec54a540e85449a357a792ff20.

### Result

Kept the Desktop-materialized PNG distinct from the differently encoded source fixture.

Changed files: None.

## Entry 000009

- Interaction: Follow-up
- Status: Completed
- Capture method: Instruction-mediated
- Continues: Entry 000008

### User input

- Final newline: None

```text
What schema version is this history using?
```

### Result

Answered that the history uses PromptSourceCode schema version 1.

Changed files: None.

## Entry 000010

- Interaction: Initial prompt
- Status: Incomplete
- Capture method: Instruction-mediated
- Status reason: Completion reason unavailable; no reliable Interrupt event was observed.

### User input

- Final newline: LF

```text
Begin a task whose completion cannot later be established.
```

## Entry 000011

- Interaction: Initial prompt
- Status: Interrupted
- Capture method: Hook-assisted
- Session ID: "fixture-session-01"
- Turn ID: "fixture-turn-09"
- Status reason: Hook-confirmed Interrupt event.

### User input

- Final newline: LF

```text
Begin a task that I will stop from the Desktop interface.
```

## Entry 000012

- Interaction: Follow-up
- Status: Completed
- Capture method: Instruction-mediated
- Continues: Entry 000011

### User input

- Final newline: LF

```text
Inspect the attached file even if its temporary source has disappeared.
```

### Artifacts

#### Artifact 1

- Kind: Attached file
- Original name (JSON): "missing.dat"
- Preservation: Unavailable
- Unavailable reason: Source data was no longer accessible when preservation was attempted.

### Result

Reported that the artifact could not be preserved and did not invent its size or hash.

Changed files: None.
