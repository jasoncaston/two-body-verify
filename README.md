# Two-body verify

A finished message is not a finished artifact. I built this to make the check concrete.

**The builder's claim is not evidence. This tool compares each claim with an artifact, a value assertion, a source, or an invocation.**

The reasoning behind the rule is taught at [DigixData Learning](https://learning.digixdata.com). This repository performs the check.

## What it does

`two-body-verify` reads a project path and a JSON claims file. It reports each claim as `evidenced`, `unsupported`, or `contradicted`, then assigns a score out of 20.

It does not edit the project. It does not fix defects. It does not grade prose quality.

## Who it is for

I made this for anyone reviewing work an agent says is complete. You name the claim, the artifact, and the check that should prove it.

## Install the package

Python 3.11 or newer is required.

```console
python3.11 -m venv .venv
.venv/bin/pip install -e .
```

## Install the plugin

After this repository is published at the named location, add its marketplace and install the plugin in Claude Code:

```text
/plugin marketplace add jasoncaston/two-body-verify
/plugin install two-body-verify@two-body-verify
```

The plugin exposes `/two-body-verify:verify-claims`.

## Run a check

```console
two-body-verify examples/verified-project examples/verified-project/claims.json
```

Use `--json` for structured output. The claims file is JSON with `version: 1`, a non-empty `claims` list, and one or more checks per claim.

```json
{
  "version": 1,
  "claims": [
    {
      "id": "report-status",
      "statement": "The report records verified status.",
      "checks": [
        {
          "kind": "file_content",
          "path": "output/report.txt",
          "contains": ["status: verified"]
        }
      ]
    }
  ]
}
```

## Example report

```text
Verification score: 20/20
Pillars: artifact 5/5, tests 5/5, sources 5/5, docs 5/5

STATUS        CLAIM                 FINDINGS
evidenced     verified-delivery     evidence matched
```

## The score

I need to be straight about the number. It measures the evidence named in the claims file, nothing more.

| Pillar | Five points requires | Why it is counted |
| --- | --- | --- |
| Artifact | The artifact exists and checked content matches. | Existence without content can preserve an empty shell. |
| Tests | Tests assert named values, with claim evidence beyond a suite result. | A green process can miss the value under review. |
| Sources | Checked external claims have a source URL recorded in an artifact. | A source makes the claim traceable. |
| Docs | A documented feature is in the implementation and in invocation evidence. | Documentation alone does not show that the path ran. |

Within each pillar, the runner awards `floor(5 * evidenced checks / checks run)`. A pillar with no checks gets zero. The four scores add to 20.

## Run these checks

| Risk | Claims check | Required evidence |
| --- | --- | --- |
| File existence or byte size used as proof | `file_content`, then `test_asserts_values` | Required file content and assertions on named values |
| PDF metadata used as proof | `pdf_visible_text` | Text captured from the rendered PDF |
| CSV formula injection | `csv_formula_safe` | Every cell safe after leading newlines are removed for inspection |
| Manifest or config name too long | `name_length_cap` | Every `name` value within the stated cap |
| Test checks only an exit code | `test_asserts_values` | Assertions on the values that close the defect |
| Documented feature never invoked | `documented_feature_invoked` | Docs text, implementation text, and invocation text |
| Passing suite used as claim proof | `suite_claim_evidence` | Passing suite record plus separate evidence of the claimed values |

The exact finding codes and check inputs are in `CHECKLIST.md`. The scoring contract is in `RUBRIC.md`.

## License

MIT. See `LICENSE`.
