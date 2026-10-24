#!/usr/bin/env python3
"""Check the authored public tree, never operator state. No network or credential loading."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ['SKILL.md', 'README.md', 'AGENT_HANDOFF.md', 'LICENSE', 'requirements.txt',
            'scripts/audit.py', 'scripts/collect.py', 'references/decision-rules.md',
            'references/weekly-contract.md', 'tests/test_audit.py', 'scripts/run_evals.py',
            'evals/evals.json', 'references/behavioral-evals.md', 'references/eval-results.md',
            'tests/test_evals.py']
PATTERNS = {
    'private-key': re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----'),
    'provider-key': re.compile(r'sk-[A-Za-z0-9_-]{24,}'),
    'github-token': re.compile(r'gh[pousr]_[A-Za-z0-9_]{24,}'),
    'jwt': re.compile(r'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}'),
    'operator-path': re.compile('/ho' + r'me/[^\s"\'<>]+|/sr' + r'v/[^\s"\'<>]+|/op' + r't/[^\s"\'<>]+'),
    'private-chat-id': re.compile(r'-100\d{8,}'),
    'private-corpus-marker': re.compile('hu' + 'man20|Sig' + 'urd|Chip' + 'CR', re.I),
    'credential-assignment': re.compile(r'(?:access_token|refresh_token|api[_-]?key)\s*[:=]\s*["\']?[A-Za-z0-9_./~+\-=]{24,}', re.I),
}

def check(root=ROOT):
    errors = []; hashes = {}
    for rel in REQUIRED:
        if not (root / rel).is_file(): errors.append((rel, 'required file absent'))
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if any(part in {'.git', '__pycache__', '.pytest_cache', '.venv'} for part in rel.parts): continue
        if rel.parts and rel.parts[0] in {'reports', 'state', 'private'}:
            errors.append((str(rel), 'operator state in public tree')); continue
        if rel.parts[:2] == ('.github', 'workflows'):
            errors.append((str(rel), 'GitHub Actions not used')); continue
        if path.is_symlink():
            errors.append((str(rel), 'unreviewed public symlink')); continue
        if not path.is_file(): continue
        raw = path.read_bytes()
        try: text = raw.decode('utf-8')
        except UnicodeError:
            errors.append((str(rel), 'unexpected binary')); continue
        for kind, pattern in PATTERNS.items():
            if pattern.search(text): errors.append((str(rel), kind))
        if re.search(r'^(?:<{7}|={7}|>{7})\s', text, re.M):
            errors.append((str(rel), 'merge conflict marker'))
        hashes[str(rel)] = hashlib.sha256(raw).hexdigest()
    print(json.dumps({'public_files': len(hashes), 'findings': errors,
                      'tree_content_sha256': hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()}, indent=2))
    return 1 if errors else 0
if __name__ == '__main__':
    raise SystemExit(check())
