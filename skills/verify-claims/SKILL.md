---
description: Run two-body-verify against a project and claims file, then report evidenced, unsupported, and contradicted claims without changing the project.
disable-model-invocation: true
argument-hint: <project-path> <claims-file>
---

The `two-body-verify` Python package is a prerequisite for this plugin. Install it before running the skill:

```console
python3.11 -m pip install "git+https://github.com/jasoncaston/two-body-verify.git@v0.1.1"
```

Before invoking the command, check for it and fail with the install instruction if it is unavailable:

```sh
if ! command -v two-body-verify >/dev/null 2>&1; then
  printf '%s\n' \
    'ERROR: two-body-verify is not installed or not on PATH.' \
    'Install it with: python3.11 -m pip install "git+https://github.com/jasoncaston/two-body-verify.git@v0.1.1"' >&2
  exit 2
fi
```

Treat `$ARGUMENTS` as exactly two paths: the project path and the claims file. Run `two-body-verify <project-path> <claims-file>`. Do not edit the project. Return the score, each claim status, and every finding exactly as the command reports them.
