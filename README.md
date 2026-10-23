# Hermes Skill Hygiene

A reusable Hermes skill and read-only auditor for maintaining a growing agent skill library without losing its operational knowledge.

The goal is not the smallest possible skill count. Keep knowledge that is unique, correct and reachable; remove duplicated doctrine, fix discovery/links, and load specialist detail only when needed.

## What it does

* Finds malformed/duplicate frontmatter, missing names/descriptions, broken local Markdown links and unreadable admitted documents.
* Inventories unique realpaths, shared-profile visibility, hashes and primary-root byte budgets.
* Supports exact-finding, source-bound review exceptions while retaining every original finding.
* Provides a lossless source-partition verifier and a conservative weekly maintenance contract.

It does not execute embedded skill instructions, delete files, change profiles, install providers, replace runtime owners or prove a skill's real-world readiness. Size and structural test results are not evidence of model-quality or latency gains.

## Install the skill

Clone this repository into an approved source location. Make the skill available using your runtime's documented local/external skill mechanism. The root SKILL.md declares the `skill-hygiene` name. When profiles share a library, install once and verify both consumers. Do not overwrite an existing checkout or skill with the same name.

Python 3.10+ and PyYAML 6+ are required for the auditor. Use an existing environment or an isolated environment outside the skill discovery tree; do not install anything just because an imported recipe says so.

## Verify

```sh
python -m unittest discover -s tests -v
python scripts/collect.py --help
python scripts/audit.py --help
python scripts/public_check.py
```

## Audit privately

For Hermes, collect through the exact managed interpreter and runtime root, not ambient PATH:

```sh
python scripts/collect.py --python "$MANAGED_PYTHON" --runtime-root "$RUNTIME_ROOT" \
  --profile "primary=$PROFILE_HOME" --platform telegram --out "$PRIVATE_DIR/catalog.json"
python scripts/audit.py --catalog "$PRIVATE_DIR/catalog.json" --deep \
  --out "$PRIVATE_DIR/audit.json" --strict
```

The collector is version-bound to installed Hermes catalog/command interfaces. A missing interface is an explicit blocker; it does not silently fall back to a different runtime. A raw filesystem fallback is available for other runtimes, but deliberately does not certify effective Hermes discovery:

```sh
python scripts/audit.py --root "$SKILL_ROOT" --deep --out "$PRIVATE_DIR/audit.json"
```

Review exceptions are a private JSON list of objects with `id`, `decision` and `reason`; allowed decisions are historical, template, source_bound, protected_owner and runtime_accepted_name. Copy the exact finding ID from a real report and explain its individual boundary. Do not generate blanket exceptions. Run with `--reviewed "$PRIVATE_DIR/reviews.json"`. A changed source invalidates its prior finding ID, including malformed frontmatter and failed reads. Error evidence participates in the overall signature. When neither bytes nor reliable file metadata can identify a source, a prior review cannot silence it. `--strict` then fails on unreviewed findings, not on explicitly retained ones; original findings and reviewed counts remain visible.

## Weekly use

Authorize and provision one job in the existing scheduler using [the weekly contract](references/weekly-contract.md). Resolve your own selectors, timezone, private origin and safety scope. On an unchanged signature stay silent. On drift inspect and perform bounded authorized maintenance, verify it, then advance successful state. Do not auto-push this repository, delete rarely used skills, disable features or touch production services.

## Inspiration and evidence limits

Inspired by [rlaope's post about periodic Hermes skill cleanup](https://x.com/rlaope/status/2113535565874540645). This repository adds ownership, preservation and verification gates; it does not claim the post supplied a performance benchmark or this implementation.

Only generic methods and synthetic tests are public here. No operator's skill corpus, receipts, reports, configs, private examples or scheduled job state are included. MIT licensed; see [LICENSE](LICENSE).
