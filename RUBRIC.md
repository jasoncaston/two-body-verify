# Verification rubric

The report scores four pillars at five points each. Every check belongs to one pillar.

| Pillar | What earns evidence | Points |
| --- | --- | ---: |
| Artifact | The artifact exists and its checked content matches the claim. | 5 |
| Tests | Tests assert the named values, and a suite result is paired with claim evidence. | 5 |
| Traceability | Every checked external claim has a recorded citation URL. | 5 |
| Docs | The documented feature is present in code and invoked by the named evidence. | 5 |

For each pillar, the runner awards `floor(5 * evidenced checks / checks run)`. A pillar with no checks receives zero, even when the pillar does not apply. A project with no traceability checks can exit 0 with every claim evidenced while scoring no more than 15/20. The total is the sum of the four pillar scores, with a maximum of 20.

## Traceability boundary

`citation_recorded` confirms that a citation URL is recorded and locatable. It does not fetch the URL, and it does not evaluate whether the source supports the claim. That judgment stays with the reviewer.

## Check inventory

| Check | Pillar | Evidence required |
| --- | --- | --- |
| `file_content` | Artifact | Required literal content in the named file |
| `pdf_visible_text` | Artifact | Required text in the rendered-text evidence |
| `csv_formula_safe` | Artifact | No formula-shaped cell, including after a leading newline |
| `name_length_cap` | Artifact | Every JSON `name` value within the stated cap |
| `test_asserts_values` | Tests | Assertions containing every required value |
| `citation_recorded` | Traceability | A locatable URL in the named citation artifact |
| `documented_feature_invoked` | Docs | Literal documentation, implementation, and invocation markers |
| `suite_claim_evidence` | Tests | A passing suite record plus separate claim-value evidence |

The score reports only what the claims file asks the runner to inspect. It does not grade prose, judgment, or project value.
