# Anti-shell checklist

Run the checks that match the claim. A check is closed only when its named evidence passes.

| Defect class | Check to run | Finding when it fails |
| --- | --- | --- |
| File shell | Run `file_content` with required strings, then run `test_asserts_values` against the test. | `file-content-not-checked` or `file-content-not-asserted` |
| PDF shell | Render the PDF, save the visible text, then run `pdf_visible_text` with the expected strings. | `pdf-visible-text-unverified` |
| CSV formula injection | Run `csv_formula_safe`. The check strips leading carriage returns and newlines before testing `=`, `+`, `-`, and `@`. | `csv-formula-injection` |
| Long manifest name | Run `name_length_cap` with the published cap. | `name-length-cap-exceeded` |
| Exit-only test | Run `test_asserts_values` with the actual values the test must assert. | `exit-code-only-test` |
| Uninvoked docs claim | Run `documented_feature_invoked` with docs, implementation, and invocation evidence. | `documented-feature-uninvoked` |
| Suite-only proof | Run `suite_claim_evidence` with a passing suite record and separate evidence containing the claimed values. | `suite-pass-not-claim-proof` |
