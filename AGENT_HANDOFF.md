# Agent handoff

Read SKILL.md, references/decision-rules.md and references/weekly-contract.md first. Resolve your own runtime/profile/source ownership. This checkout is a workflow and read-only auditor, not an autonomous delete service.

Install PyYAML in an existing approved Python environment if absent. Run `python -m unittest discover -s tests -v`. Use `scripts/collect.py --help` only under the declared Hermes interpreter/runtime root, then audit the private catalog. For another runtime, provide its canonical catalog or use the explicitly weaker physical fallback.

All reports/state/fixtures from a real operator are private and must remain outside the public tree. Before publication, check commit metadata as well as file contents: use an explicitly approved public identity, preferably an agent/noreply identity, and do not assume an ambient global Git email is public. Replacing live refs does not guarantee erasure of cached or otherwise accessible old Git objects. The included tests create synthetic temporary libraries and perform no provider calls, installs, domain effects or publication. There are no GitHub Actions workflows. Re-run tests, the authoring guard, diff checks and the public-surface scan before publication. Read back remote visibility, HEAD and tree, not only the push result.
