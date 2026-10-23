#!/usr/bin/env python3
"""Read-only skill hygiene audit. Reports are private operator artifacts, not publication inputs."""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import urllib.parse
import yaml

EXCLUDED = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.pytest_cache', 'vendor', 'dist', 'build'}
SUPPORT = {'references', 'scripts', 'assets', 'templates'}
MAX_BYTES = 2 * 1024 * 1024

class DuplicateKey(ValueError):
    pass

class StrictLoader(yaml.SafeLoader):
    pass

def strict_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise DuplicateKey('duplicate frontmatter key: ' + str(key))
        result[key] = loader.construct_object(value_node, deep=deep)
    return result
StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, strict_mapping)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def frontmatter(text):
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)', text, re.S)
    if not match:
        raise ValueError('missing YAML frontmatter')
    result = yaml.load(match.group(1), Loader=StrictLoader)
    if not isinstance(result, dict):
        raise ValueError('frontmatter must be a mapping')
    return result

def outside_code(text):
    lines = []; fence = None
    for line in text.splitlines():
        match = re.match(r'^\s{0,3}(`{3,}|~{3,})(.*)$', line)
        if match:
            run, tail = match.groups()
            if fence is None:
                fence = (run[0], len(run))
            elif run[0] == fence[0] and len(run) >= fence[1] and not tail.strip():
                fence = None
            continue
        if fence is None:
            lines.append(re.sub(r'(`+).*?\1', '', line))
    return '\n'.join(lines)

def relative_links(text):
    for raw in re.findall(r'\]\(\s*([^\s)]+)(?:\s+[^)]*)?\)', outside_code(text)):
        if raw.startswith('<') and raw.endswith('>'):
            raw = raw[1:-1]
        try:
            target = urllib.parse.urlsplit(raw)
        except ValueError:
            continue
        if target.scheme or target.netloc or not target.path:
            continue
        path = urllib.parse.unquote(target.path)
        if any(char in path for char in '<>{}$*'):
            continue
        if path.startswith(('path/to/', '/path/to/', 'some/path/', 'your-project/')):
            continue
        yield raw, path

def physical_entries(roots):
    """Fallback only. Hermes users must pass the canonical runtime catalog instead."""
    entries = []
    for root in roots:
        root = Path(root).resolve()
        if not root.is_dir():
            raise ValueError('root is not an existing directory: ' + str(root))
        for directory, dirs, files in os.walk(root, followlinks=False):
            has_skill = 'SKILL.md' in files
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not (has_skill and d in SUPPORT))
            if has_skill:
                entries.append({'path': str(Path(directory) / 'SKILL.md'), 'discovery': 'physical_fallback'})
    return entries

def source_owner(path):
    for parent in (path.parent, *path.parents):
        if (parent / '.git').exists():
            return 'repository-bound'
    return 'local-or-external; verify receipt before mutation'

def source_identity(path, raw=None):
    """Bind even failed parses/reads; an unidentifiable source cannot be silenced."""
    if raw is not None:
        return {'source_sha256': digest(raw), 'identity_reliable': True}
    try:
        st = path.stat()
    except OSError:
        return {'stat_signature': None, 'identity_reliable': False}
    return {'stat_signature': [st.st_dev, st.st_ino, st.st_uid, st.st_mode,
                               st.st_size, st.st_mtime_ns, st.st_ctime_ns],
            'identity_reliable': True}

def audit(entries, deep=False, max_files=50000):
    findings = []; advisories = []; records = []; file_records = []; seen = set(); seen_docs = set(); finding_ids = set()
    def finding(kind, path, **extra):
        body = {'kind': kind, 'path': str(path), **extra}
        body['id'] = digest(json.dumps(body, sort_keys=True).encode())
        if body['id'] not in finding_ids:
            findings.append(body)
            finding_ids.add(body['id'])
    def read(path):
        if path.stat().st_size > MAX_BYTES:
            raise ValueError('file exceeds finite read budget')
        return path.read_bytes()
    def document(path):
        real = path.resolve()
        if real in seen_docs:
            return
        seen_docs.add(real)
        if len(seen_docs) > max_files:
            raise ValueError('document budget exhausted; scan is incomplete')
        raw = None
        try:
            raw = read(real); text = raw.decode('utf-8')
            file_records.append({'path': str(real), 'sha256': digest(raw), 'bytes': len(raw)})
            for link, target in relative_links(text):
                if target.startswith('/'):
                    advisories.append({'kind': 'web_root_relative_link', 'path': str(real), 'link': link, 'meaning': 'resolve against the documented web origin; do not guess a host filesystem path'})
                elif not (real.parent / target).exists():
                    finding('broken_relative_link', real, link=link, source_sha256=digest(raw))
        except (OSError, UnicodeError, ValueError) as error:
            finding('unreadable_document', real, detail=type(error).__name__, **source_identity(real, raw))
    grouped = {}
    for entry in entries:
        key = str(Path(entry['path']).absolute().resolve())
        if key not in grouped:
            grouped[key] = {**entry, 'effective_profiles': []}
        grouped[key]['effective_profiles'] = sorted(set(grouped[key]['effective_profiles']) | set(entry.get('effective_profiles', [])))
    for entry in sorted(grouped.values(), key=lambda e: str(e['path'])):
        lexical = Path(entry['path']).absolute(); path = lexical.resolve()
        if path in seen:
            continue
        seen.add(path)
        raw = None
        try:
            raw = read(path); text = raw.decode('utf-8'); fm = frontmatter(text)
            name = fm.get('name'); description = fm.get('description')
            if not isinstance(name, str) or not name.strip():
                finding('missing_name', path, source_sha256=digest(raw))
                name = path.parent.name
            if not isinstance(description, str) or not description.strip():
                finding('missing_description', path, source_sha256=digest(raw))
            if isinstance(name, str) and not re.fullmatch(r'[A-Za-z0-9._-]+', name):
                finding('invalid_name', path, source_sha256=digest(raw))
            if len(raw) > 24000:
                advisories.append({'kind': 'large_root_review', 'name': name, 'bytes': len(raw), 'path': str(path), 'meaning': 'not evidence of redundancy; preserve unique procedures and safety gates'})
            explicit = 'Use only' in str(description) or 'explicit' in str(description).lower()
            classification = 'retain-explicit-compatibility' if explicit else 'retain-owner-workflow'
            records.append({'name': name, 'path': str(path), 'lexical_path': str(lexical), 'sha256': digest(raw), 'bytes': len(raw), 'owner': source_owner(path), 'disposition': classification, 'effective_profiles': entry.get('effective_profiles', [])})
            document(path)
            if deep:
                refs = path.parent / 'references'
                if refs.exists():
                    for directory, dirs, files in os.walk(refs, followlinks=False):
                        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED)
                        for filename in sorted(files):
                            if filename.lower().endswith('.md'):
                                document(Path(directory) / filename)
        except (OSError, UnicodeError, ValueError, yaml.YAMLError, TypeError) as error:
            finding('invalid_root', path, detail=type(error).__name__, **source_identity(path, raw))
    by_path = collections.defaultdict(list)
    for f in findings:
        by_path[f['path']].append(f['kind'])
    for record in records:
        if record['path'] in by_path:
            record['disposition'] = 'repair-or-owner-reviewed-exception'
    signature = digest(json.dumps({'documents': sorted(file_records, key=lambda f: f['path']), 'error_and_finding_evidence': sorted(findings, key=lambda f: f['id']), 'entries': sorted((str(e['path']), e.get('resolution_status', ''), sorted(e.get('effective_profiles', []))) for e in entries)}, sort_keys=True).encode())
    return {'schema_version': 1, 'discovery': 'caller-supplied catalog; verify it came from the managed runtime', 'deep': deep, 'unique_roots': len(seen), 'readable_roots': len(records), 'documents_read': len(file_records), 'signature': signature, 'records': records, 'documents': file_records, 'findings': findings, 'advisories': advisories, 'counts': dict(collections.Counter(f['kind'] for f in findings)), 'boundary': 'read-only structural evidence; no semantic disuse, deletion, readiness, latency, model-quality or live-delivery claim'}

def verify_partition(original, parts):
    """Each source byte must appear once in ordered slices, with no gaps/overlap."""
    cursor = 0
    for part in sorted(parts, key=lambda p: p['start']):
        start, end = part['start'], part['end']
        if start != cursor or end <= start or end > len(original):
            raise ValueError('source coverage gap, overlap or invalid range')
        target = Path(part['path']).read_bytes()
        if original[start:end] not in target:
            raise ValueError('source bytes not preserved in declared target')
        cursor = end
    if cursor != len(original):
        raise ValueError('source coverage incomplete')
    return True

def evaluate_reviews(report, decisions):
    """An exception is exact-finding/hash bound, explicit and never removes the evidence."""
    allowed = {'historical', 'template', 'source_bound', 'protected_owner', 'runtime_accepted_name'}
    indexed = {}
    for item in decisions:
        if item.get('decision') not in allowed or not str(item.get('reason', '')).strip():
            raise ValueError('invalid or unexplained review decision')
        if item.get('id') in indexed:
            raise ValueError('duplicate review decision')
        indexed[item['id']] = item
    reviewed = []; unreviewed = []
    current_ids = {finding['id'] for finding in report['findings']}
    for finding in report['findings']:
        if finding['id'] in indexed and finding.get('identity_reliable', True):
            reviewed.append({'finding': finding, 'review': indexed[finding['id']]})
        else:
            unreviewed.append(finding)
    return {'reviewed': reviewed, 'unreviewed': unreviewed,
            'stale_decision_ids': sorted(set(indexed) - current_ids)}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, help='JSON list of canonical entries, or object containing entries/rows')
    parser.add_argument('--root', action='append', default=[], help='physical fallback; not proof of Hermes-effective discovery')
    parser.add_argument('--deep', action='store_true')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--reviewed', type=Path, help='private exact-finding review decisions; retained findings remain visible')
    parser.add_argument('--strict', action='store_true', help='nonzero exit when unreviewed structural findings remain')
    args = parser.parse_args(argv)
    if args.catalog:
        data = json.loads(args.catalog.read_text()); entries = data if isinstance(data, list) else data.get('entries', data.get('rows'))
        if not isinstance(entries, list):
            parser.error('catalog must contain entries')
    elif args.root:
        entries = physical_entries(args.root)
    else:
        parser.error('provide --catalog or --root')
    report = audit(entries, deep=args.deep)
    decisions = json.loads(args.reviewed.read_text()) if args.reviewed else []
    report['review'] = evaluate_reviews(report, decisions)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    os.chmod(args.out, 0o600)
    print(json.dumps({**{k: report[k] for k in ['unique_roots', 'readable_roots', 'documents_read', 'signature', 'counts']}, 'unreviewed_findings': len(report['review']['unreviewed']), 'reviewed_retained_findings': len(report['review']['reviewed'])}))
    return 1 if args.strict and report['review']['unreviewed'] else 0
if __name__ == '__main__':
    raise SystemExit(main())
