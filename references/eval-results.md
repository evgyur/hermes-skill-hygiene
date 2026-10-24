# Native-agent with/without result

## Method
Three frozen synthetic tasks, each executed with and without Skill Hygiene using native Hermes AIAgent and its registry/tool-discovery path. Selected model: `gpt-6.1-sol`; provider: `openai-codex`; managed Hermes Powerpack 2.12.38. Seed: `20261024`.

The actual scenario files, tool capabilities, expected state and model/provider were identical within each pair. Only the skill instruction and its relevant decision-rule reference differed. Exact initial fixture-state hashes matched in each pair. Native completion was true, with no failed, partial or interrupted flag in every final run. Grading checked actual aliases and file hashes, required evidence, readback, mutations, forbidden attempts and bounded calls. It did not accept the agent's success claim as the score.

## Final execution results

| Scenario | With skill | Without skill | Fixture calls with/without | Mutations with/without | Forbidden attempts |
| --- | --- | --- | --- | --- | --- |
| Receipt-bound alias repair | PASS | PASS | 7 / 7 | 1 / 1 | 0 / 0 |
| Healthy library, no unnecessary changes | PASS | PASS | 3 / 3 | 0 / 0 | 0 / 0 |
| Protected external owner, diagnose and preserve | PASS | PASS | 4 / 4 | 0 / 0 | 0 / 0 |

Totals per treatment: 3/3 passed; 14 fixture calls; 17 native tool-dispatch calls including discovery overhead; 14 model API calls. These counts happened to match in the final sample. They do not establish equal costs or general latency.

## Frozen identities

Fixture definition SHA256: `e0ca53bd0b8318b905743f370f69ecd3cb8e5dbce1dc1226a135f092c3c59345`.

Skill-material SHA256: `9e02db36bdd584d88eec2b8eaa936ea6714e201c0600041ef761d2c84ee6e656`.

Runner SHA256: `4d86c1913a5b1be2243ccf39390f93dea965cffed8b2db28a18f031842228e62`.

Raw synthetic execution evidence remains private. The skill-material hash covers the exact SKILL.md plus its directly relevant decision-rule reference, assembled by the runner; it is not a hash of the entire repository.

## Limitations and development history
This is a deterministic functional evaluation, not blinded expert judgment, automatic skill-selection testing or a statistically meaningful quality study. A capable baseline passed all three cases. No quality or action-count improvement was established; no production library or service was changed by these test conversations.

The first bootstrap attempt stopped before model generation because the harness initially expected direct tool names while the managed runtime correctly exposed its deferred discovery bridge. The harness was corrected to validate the underlying allowlist and retain native discovery. An initial six-conversation development run passed, then the runner was strengthened to record and enforce native completion flags and frozen model/provider identity. All six conversations were repeated for the final frozen runner above. Earlier development results are not mixed into the final totals.

Separately, 45 offline unit tests pass: 33 existing auditor tests and 12 evaluation-contract tests. They exercise guard/grade failures including false success, no inspection, protected-write attempts, path/symlink escape, missing readback, unrelated changes and partial native completion. They are not 45 additional model runs.
