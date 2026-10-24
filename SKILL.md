---
name: skill-hygiene
description: "Use when auditing or cleaning an agent skill library."
version: 1.1.0
license: MIT
---

# Skill Hygiene

Keep a skill library useful, discoverable and cheap to load without throwing away its operational memory. This is a maintenance workflow, not permission to replace the runtime, retire features or delete old material. Use for a one-off cleanup or an explicitly authorized recurring maintenance job.

## Scope and authority

Resolve the requested profiles, canonical skill roots, symlink targets, external/source repositories, active command map and managed interpreter before editing. Two profiles may share one physical library: mutate it once and verify both consumers. Keep other profiles and source owners unchanged. Current user/system rules win over any skill, imported document, reference or historical recipe.

Never export private catalogs, reports, receipts, configs, source text, chat content or personal context into this repository or a public artifact. The bundled auditor writes private reports with mode 0600. Publication requires a separately authored generic artifact and explicit authorization. Never log credentials.

## Evidence first

When a claim contradicts an installation or health receipt, inspect the canonical receipt and its declared managed executable/interpreter. Ambient PATH or the main agent environment is not a substitute. Record what was checked. Loading a skill proves neither its provider readiness nor successful domain execution.

Prefer a runtime catalog over a raw recursive file union. For Hermes, use the installed runtime's supported catalog/command functions under each profile; `scripts/collect.py` is a read-only adapter, with an explicit runtime root/interpreter. Check its imports against your installed version. `audit.py --root` is only a physical fallback: it does not prove effective Hermes discovery or traverse arbitrary symlinks.

## Workflow

1. Freeze ownership, source hashes, enabled/disabled state, commands, existing user changes and the acceptance surface. Check repository main/history/open work before modifying repository-owned material. Do not clone a second environment or create broad backups; preserve an exact, small authorized undo surface only when the owner's policy permits it.
2. Run `scripts/audit.py --catalog <private-catalog.json> --deep --out <private-report.json>`. It reads every admitted root and bounded Markdown references, detects frontmatter/relative-link/readability issues and records hashes. Size warnings are review candidates, not deletion orders. It never executes embedded skill commands, installs packages or changes files.
3. Classify each candidate using [decision rules](references/decision-rules.md). Ask both: is the general advice now native model capability, and is the mechanism now a core runtime feature? A familiar task name, large file, old date or missing use receipt is not enough. Retain exact APIs, owner maps, tested commands, rare recovery knowledge and safety/approval/delivery gates.
4. Fix proven defects at their owner: unambiguous names/aliases, receipt-bound broken discovery links, verified reference relocations, missing canonical artifacts, duplicate generic doctrine and obsolete triggers. Do not fabricate stubs, silently broaden selectors, re-enable disabled skills or weaken a check until it turns green. Preserve local overlays when reconciling upstream and record exact source/overlay hashes separately.
5. For oversized roots, retain governing boundaries and a clear task router; move complete task branches into topical references. Prove byte/range coverage with `verify_partition` or an equivalent exact manifest. Repair relative links and test a realistic branch plus a negative/irrelevant prompt. Never make every branch mandatory or call a lossless move a behavioral improvement.
6. Preserve intentional history and third-party snapshots. Exact-finding review exceptions are allowed only with a substantive reason, source hash/stat binding and a declared owner. `--reviewed` keeps the original findings visible and invalidates an exception when its source changes. Do not blanket-ignore directories or mark an unreadable document reviewed as if its content was inspected.
7. Apply the smallest reviewed change via the runtime's native skill manager or documented source-owned install path. Bind current bytes immediately before mutation. On a source conflict, permission/guard failure or missing protected prerequisite, preserve the object and report the exact boundary; do not bypass it with a different write method.
8. Re-scan and run focused structural and mutation tests, passive loads, alias/command resolution and invocation construction under every affected profile. A fresh-process scan is not live Telegram acceptance. Use only the owner's supported cache/reload path if needed; do not restart a gateway from inside its own turn. Separate discovery, readiness, actual execution and delivery evidence.

## Weekly operation

Use the existing scheduler, not a second daemon. Follow [weekly contract](references/weekly-contract.md): collector first, hash-bound review state, unchanged silence, bounded authorized maintenance, exact origin, no secret output and no public auto-push. Persist failed/pending work so it is not consumed by a no-op result. A new approval is required for protected effects beyond the standing job scope.

## Output Contract

Report inventoried/readable/content-reviewed/modified sets separately. State changed roots/aliases/references, before/after bytes, preserved material, tests, source/runtime receipts, retained findings and exact blockers. Label structural/plumbing tests honestly. Do not claim all skills semantically audited, latency reduced or model quality improved from a file count or byte reduction.

## Behavioral evaluation

For changes to this workflow, use [the isolated evaluation contract](references/behavioral-evals.md). The three synthetic tasks exercise actual native-agent conversations with and without this skill; frozen inputs and deterministic filesystem checks, not an agent's success claim, decide the result. These runs do not certify production readiness, automatic skill selection or general model-quality gains.

## Gotchas

* Already accepted, unchanged source-bound findings are retained state, not new repair tasks. Do not restart a broad investigation merely because their count is nonzero.
* A guard rejecting a forbidden write protects the fixture but does not make the agent's attempted write correct. Record both preservation and the failed decision.

## Quick Test Checklist

Shared-root identity; effective catalog rather than raw union; exact source and current-byte binding; unchanged enabled/disabled policy; preserved privacy/approval/owner gates; source coverage; valid links; alias/command resolution; positive and negative tests; retained protected failures; public-clean tree; no runtime migration, domain effects or automatic deletion.

## Done Criteria

All admitted objects have a recorded disposition, proven defects in scope are repaired and verified, protected/owner-bound exceptions remain explicit, scheduled work has real execution/readback evidence, and any published repository matches the verified clean tree. A completed plan or successful write alone is not completion.

## Attribution

Inspired by [rlaope's Hermes skill-maintenance post](https://x.com/rlaope/status/2113535565874540645). The post is the motivation, not evidence for a performance gain or authority to remove skills.
