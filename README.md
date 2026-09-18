# PromptSourceCode

> The prompt history is the new source code.

Most AI-assisted projects keep the finished files but lose the conversation that shaped
them. PromptSourceCode keeps that story with the project: what you asked for, what you
changed your mind about, what you attached, and what the agent ultimately did.

That makes it easier for you, or the next person, to understand not only *what* was built,
but *why* and *how* it was built that way.

## Why use it?

PromptSourceCode helps you:

- remember the decisions behind AI-generated work;
- preserve follow-up requests, corrections, and changes of direction;
- keep useful copies of files and images that were part of the conversation;
- review a project's history in an ordinary readable file; and
- keep that history local unless you explicitly decide to share it.

PromptSourceCode is designed for local projects used with Codex Desktop. Other coding
agent harnesses are not currently supported.

## Install

Requires a local Git project on macOS, Codex Desktop, and `/usr/bin/python3`
(tested with Python 3.9.6). No Python packages need to be installed.

1. Download **Source code (zip)** from the
   [PromptSourceCode 0.2.0 release](https://github.com/ironwood-lang/prompt-source-code/releases/tag/v0.2.0)
   and unzip it.
2. From the downloaded folder, run:

   ```text
   /usr/bin/python3 scripts/instruction_contract.py install "/path/to/your/project"
   /usr/bin/python3 scripts/instruction_contract.py check "/path/to/your/project"
   ```

   This appends a small marked loader to the root `AGENTS.md` without replacing existing
   instructions and installs the capture contract at
   `.prompt-source/instructions-v1.md` plus its project-local capture helper at
   `.prompt-source/validate.py`.
3. Review the three installed files, then open the project in Codex Desktop and start a
   new task.

That is the complete standard installation. It uses only project files and the system
Python standard library—no global Codex configuration, hook, skill, plugin, background
service, or network service.

Already using 0.1.0 or a development candidate? Follow the
[update instructions](docs/INSTALLATION.md#3-update-the-loader-and-dedicated-instructions)
to preserve your existing project guidance and history.

## Try it

Send this prompt in a new Codex Desktop task:

```text
Create a file named hello.txt containing: Hello from PromptSourceCode!
```

After Codex finishes, look in your project root for `PROMPT_SOURCE.md`. It should contain
the request you sent and a short account of the result. The new `hello.txt` remains an
ordinary project file.

If you later send a follow-up such as:

```text
Change the message to: Hello, prompt history!
```

the follow-up is added as a new part of the history. The original request remains visible
instead of being replaced.

## A simple example

Imagine that you ask Codex to add a dark theme, then ask for blue accents, and finally
correct that choice to green. The finished interface shows only the final design.
PromptSourceCode preserves the full path:

1. Add a dark theme.
2. Use blue accents.
3. Correction: use green accents instead.
4. Record what changed.

Someone reviewing the project later can see that green was a deliberate correction, not
an unexplained implementation detail.

## Your history stays under your control

PromptSourceCode keeps its generated history in your local project. It does not
automatically commit, push, publish, or upload that history. Your normal project files
continue to work with Git as usual.

Review the generated history before deciding whether you want to share it. Prompts and
attachments can contain private or sensitive information.

## Optional enhanced capture

The standard installation above is enough for normal use. An optional advanced setup can
improve exact prompt matching and record trusted Stop-button interruptions. It requires
separate review and activation; see the
[optional hooks guide](docs/OPTIONAL_HOOKS.md) when you are ready.

## Test it and tell us how it went

Please try the same path a new user would:

- download and unzip PromptSourceCode;
- install the loader and dedicated instructions in a new local project;
- send the example prompt and one follow-up in Codex Desktop;
- confirm the history is easy to find and understand; and
- confirm your ordinary project files still behave normally.

If anything is confusing or does not work, [open an issue](https://github.com/ironwood-lang/prompt-source-code/issues)
and describe the step where you got stuck.

## More help

- [Complete installation, updating, disabling, removal, and troubleshooting](docs/INSTALLATION.md)
- [Compatibility and supported environments](docs/COMPATIBILITY.md)
- [Technical reference for maintainers and advanced users](docs/TECHNICAL_REFERENCE.md)
- [What's new in 0.2.0](docs/RELEASE_NOTES_0.2.0.md)

## License

PromptSourceCode is available under the terms in [LICENSE](LICENSE).
