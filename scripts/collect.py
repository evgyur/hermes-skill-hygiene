#!/usr/bin/env python3
"""Collect canonical file-based Hermes catalogs through an explicitly admitted managed runtime."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess

CHILD = r'''
import json, os, sys
from tools.skills_tool import _skill_catalog
from agent.skill_commands import get_skill_commands
from agent.skill_utils import get_disabled_skill_names
rows = []
disabled = get_disabled_skill_names()
for item in _skill_catalog(skip_disabled=True, include_hidden=True):
    active = (item['name'] not in disabled and item.get('load_name') not in disabled
              and item.get('load_name') is not None)
    rows.append({'path': str(item['path']), 'name': item['name'],
                 'resolution_status': item['status'], 'load_name': item.get('load_name'),
                 'effective_profiles': [os.environ['HYGIENE_PROFILE']] if active else []})
print(json.dumps({'entries': rows, 'commands': get_skill_commands(),
                  'disabled': sorted(disabled), 'runtime': sys.executable}, default=str))
'''

def collect(python, runtime_root, profiles, platform='cli'):
    python = Path(python).absolute(); runtime_root = Path(runtime_root).resolve()
    if not python.is_file() or not runtime_root.is_dir():
        raise ValueError('managed interpreter/runtime root does not exist')
    all_entries = {}; results = []
    for name, home in profiles:
        home = Path(home).resolve()
        if not name or not home.is_dir():
            raise ValueError('invalid admitted profile')
        env = os.environ.copy()
        env.update(HERMES_HOME=str(home), HERMES_PLATFORM=platform,
                   HYGIENE_PROFILE=name, PYTHONPATH=str(runtime_root), PYTHONDONTWRITEBYTECODE='1')
        result = subprocess.run([str(python), '-c', CHILD], cwd=runtime_root, env=env,
                                capture_output=True, text=True, timeout=180, check=False)
        if result.returncode:
            raise RuntimeError('managed catalog failed for ' + name + '; exit=' + str(result.returncode) + '; inspect protected local stderr, never substitute an ambient-runtime scan')
        try:
            data = json.loads(result.stdout)
        except (ValueError, TypeError) as error:
            raise RuntimeError('managed catalog emitted non-JSON output for ' + name) from error
        rows = data.get('entries')
        if not isinstance(rows, list):
            raise ValueError('managed catalog has no entries')
        results.append({'name': name, 'home': str(home), 'runtime': data['runtime'],
                        'scanned': len(rows), 'commands': data['commands'],
                        'disabled': data['disabled'], 'warning_lines': len(result.stderr.splitlines())})
        for row in rows:
            key = str(Path(row['path']).resolve())
            if key not in all_entries:
                all_entries[key] = {**row, 'path': key, 'effective_profiles': []}
            all_entries[key]['effective_profiles'] = sorted(set(all_entries[key]['effective_profiles']) | set(row['effective_profiles']))
    return {'schema_version': 1, 'discovery': 'managed Hermes file-based catalog',
            'runtime_root': str(runtime_root), 'profiles': results,
            'entries': sorted(all_entries.values(), key=lambda e: e['path']),
            'limitations': ['Package/plugin-owned projections and core commands are separate owners; do not modify them as user-local files. No provider readiness or live message execution is claimed.']}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python', required=True, type=Path)
    parser.add_argument('--runtime-root', required=True, type=Path)
    parser.add_argument('--profile', action='append', required=True, help='name=profile-home; repeat for admitted profiles')
    parser.add_argument('--platform', default='cli')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    profiles = []
    for item in args.profile:
        if '=' not in item:
            parser.error('profile must be name=home')
        profiles.append(item.split('=', 1))
    if len({name for name, home in profiles}) != len(profiles):
        parser.error('profile names must be unique')
    data = collect(args.python, args.runtime_root, profiles, args.platform)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    os.chmod(args.out, 0o600)
    print(json.dumps({'profiles': len(profiles), 'unique_roots': len(data['entries']), 'scope': 'file-based catalog only'}))
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
