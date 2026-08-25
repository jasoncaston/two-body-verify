# Two-body verify

A finished message is not a finished artifact. I built this to make the check concrete.

**The builder's claim is not evidence. This tool compares each claim with an artifact, a value assertion, a recorded citation, or an invocation.**

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

Run the first-pass claim:

```console
two-body-verify . examples/claims-first.json
```

Then run the corrected claim:

```console
two-body-verify . examples/claims-corrected.json
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

## Watch it catch the gap

The first claim checks this repository's traceability boundary but never names the README content that proves it. The runner gives the test and docs pillars credit, then names the missing content check.

```text
Verification score: 10/20
Pillars: artifact 0/5, tests 5/5, traceability 0/5, docs 5/5

STATUS        CLAIM                 FINDINGS
unsupported   traceability-boundary file-content-not-checked
  file-content-not-checked [README.md]: File existence alone does not verify its content.
```

The corrected claim names the required README statement. It passes while the empty traceability pillar remains zero:

```text
Verification score: 15/20
Pillars: artifact 5/5, tests 5/5, traceability 0/5, docs 5/5

STATUS        CLAIM                 FINDINGS
evidenced     traceability-boundary evidence matched
```

## The score

I need to be straight about the number. It measures the evidence named in the claims file, nothing more.

| Pillar | Five points requires | Why it is counted |
| --- | --- | --- |
| Artifact | The artifact exists and checked content matches. | Existence without content can preserve an empty shell. |
| Tests | Tests assert named values, with claim evidence beyond a suite result. | A green process can miss the value under review. |
| Traceability | Checked external claims have a citation URL recorded in an artifact. | A recorded URL makes the citation locatable. |
| Docs | A documented feature is in the implementation and in invocation evidence. | Documentation alone does not show that the path ran. |

Within each pillar, the runner awards `floor(5 * evidenced checks / checks run)`. A pillar with no checks gets zero, even when that pillar does not apply to the project. A project with no traceability checks can pass every claim and exit 0 while scoring no more than 15/20. The score is coverage-sensitive, not a universal quality grade.

## Traceability stops here

`citation_recorded` confirms that a citation URL is recorded and locatable. It does not fetch the URL, and it does not evaluate whether the source supports the claim. That judgment stays with the reviewer.

## Run these checks

| Risk | Claims check | Required evidence |
| --- | --- | --- |
| File existence or byte size used as proof | `file_content`, then `test_asserts_values` | Required file content and assertions on named values |
| PDF metadata used as proof | `pdf_visible_text` | Text captured from the rendered PDF |
| CSV formula injection | `csv_formula_safe` | Every cell safe after leading newlines are removed for inspection |
| Manifest or config name too long | `name_length_cap` | Every `name` value within the stated cap |
| Test checks only an exit code | `test_asserts_values` | Assertions on the values that close the defect |
| Citation is absent or cannot be located | `citation_recorded` | A URL recorded in the named citation artifact |
| Documented feature never invoked | `documented_feature_invoked` | Docs text, implementation text, and invocation text |
| Passing suite used as claim proof | `suite_claim_evidence` | Passing suite record plus separate evidence of the claimed values |

The exact finding codes and check inputs are in `CHECKLIST.md`. The scoring contract is in `RUBRIC.md`.

## Limitations

The runner's claim-to-evidence matching is literal substring matching. It cannot follow a feature through a dispatcher, registry, plugin table, reflection, or another indirect invocation path. When the implementation uses one of those patterns, the reviewer must supply direct evidence or treat the result as unresolved.

## License

MIT. See `LICENSE`.
