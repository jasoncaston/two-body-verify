---
description: Run two-body-verify against a project and claims file, then report evidenced, unsupported, and contradicted claims without changing the project.
disable-model-invocation: true
argument-hint: <project-path> <claims-file>
---

Treat `$ARGUMENTS` as exactly two paths: the project path and the claims file. Run `two-body-verify <project-path> <claims-file>`. Do not edit the project. Return the score, each claim status, and every finding exactly as the command reports them.
