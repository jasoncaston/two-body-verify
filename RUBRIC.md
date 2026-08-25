# Verification rubric

The report scores four pillars at five points each. Every check belongs to one pillar.

| Pillar | What earns evidence | Points |
| --- | --- | ---: |
| Artifact | The artifact exists and its checked content matches the claim. | 5 |
| Tests | Tests assert the named values, and a suite result is paired with claim evidence. | 5 |
| Sources | Every checked external claim has a recorded source URL. | 5 |
| Docs | The documented feature is present in code and invoked by the named evidence. | 5 |

For each pillar, the runner awards `floor(5 * evidenced checks / checks run)`. A pillar with no checks receives zero. The total is the sum of the four pillar scores, with a maximum of 20.

The score reports only what the claims file asks the runner to inspect. It does not grade prose, judgment, or project value.
