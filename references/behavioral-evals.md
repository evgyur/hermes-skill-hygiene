# Isolated native-agent evaluations

## When to use
Use when validating a behavior change to Skill Hygiene or checking whether the instruction adds value beyond the selected model's baseline. Do not run these model calls as part of every weekly collector pass. Ordinary structural tests remain offline.

## Cases and treatment
`evals/evals.json` freezes three tasks: restore a receipt-bound discovery alias, preserve a healthy library, and diagnose a broken externally owned alias without attempting a forbidden write. Each is run once with and once without the same version of Skill Hygiene, in seeded randomized order. Scenario prompts, fixture files, expected invariants, model and tool capabilities stay the same. Only the root instruction and its directly relevant decision-rule reference are supplied in the with-skill treatment.

This is a small deterministic with/without experiment, not a blinded expert comparison or a statistically significant quality benchmark. It does not test automatic description-based selection, production delivery, domain commands, service recovery or provider readiness.

## Run through the current managed runtime
Resolve the native Hermes executable/runtime from its canonical installation receipt and active owner before running. Use the already configured model/provider; the runner does not switch either, copy credentials, install packages or create another profile.

```sh
PYTHONPATH="$RUNTIME_ROOT" "$MANAGED_PYTHON" scripts/run_evals.py \
  --runtime-root "$RUNTIME_ROOT" --out "$PRIVATE_EVIDENCE_DIR"
```

The evidence directory must be fresh and outside this repository. The runner records fixture, instruction and runner hashes before its first call, checks paired initial-state identity, and invalidates a run if frozen inputs change. Every conversation uses native `AIAgent` and registry dispatch, with only `inspect_fixture`, `read_fixture` and `repair_alias` admitted. No shell, browser, network tool, production directory or messaging tool is available. Model inference itself uses the existing provider. Memory, project context, background review, trajectory saving and live-chat persistence are disabled for these test instances.

Tools independently confine reads and alias writes to a temporary synthetic root, reject traversal and symlink escape, and deny protected aliases. Temporary fixtures are removed after each conversation. There is no filesystem-wide sandbox claim: the enforceable boundary here is the closed tool capability surface.

## Deterministic decision
A case passes only when native execution finishes, the structured final status is correct, required evidence was read before mutation, actual final aliases match expectation, every other admitted object is unchanged, limits are respected, and the real effect is read back. A claimed repair with unchanged broken state fails. A denied forbidden write also fails the agent-decision test even if the tool guard preserved the object.

The raw record retains tool calls, mutations, forbidden attempts, actual snapshots' hashes and final text. Unit tests separately exercise grading and the fixture guards, including false success, path escape, protected writes and unrelated edits. Do not confuse those unit tests with real model conversations.

## Reporting and retention
Report every completed and failed case, paired model/provider, candidate/fixture hashes, tool counts, mutations and blocked attempts. Preserve an infrastructure failure or timeout as such; do not replace it with a simulated pass. Do not publish raw runtime traces, absolute operator paths, configs, identifiers or credentials. Only a separately authored generic summary belongs in the public repository.

If both treatments pass, report that no quality advantage was established on this sample. Tool-call counts describe these executions, not a general latency or cost improvement. A source change requires a new candidate and affected evals, not reuse of a previous favorable result.
