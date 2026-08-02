# Project agent memory

This file is the project's committed home for project-intrinsic agent knowledge: build, test, release, architecture, and sharp-edge notes that should travel with the code.

- This app runs on `splunk_input_runtime` (https://github.com/Bre77/splunk-input-runtime), not `splunklib`/`splunk-sdk`. `lib/requirements.txt` pins it to an exact commit archive URL with a `sha256:` hash recorded in a comment above it (no PyPI package exists yet, so there is no `==version` line to pin against). Bump both the commit and the recorded hash together when the runtime releases a new version; never point at a branch.
- This app stores no credential and never touches `storage/passwords`, so it has no `self.context.credentials` usage and no `Script.service` need - the runtime deliberately does not expose `.service`.
- `.build.sh` vendors `lib/` fresh on every build (`pip install -t lib -r lib/requirements.txt --no-dependencies`); `lib/` is gitignored except `lib/requirements.txt`. Do not commit vendored packages into `lib/`.
- The runner (`Script.run_script`) owns `EventWriter.close()`; app code must not call it explicitly.
- `Bre77/SplunkUI-devcontainer`'s `test-harness/verify-splunklib-app.sh` is app-agnostic - point it at this repo to get a `dependency=splunk_input_runtime` build+import check on both Python 3.9 and 3.13.

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
