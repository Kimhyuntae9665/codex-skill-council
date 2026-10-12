"""Offline package completeness, hash, link and configuration checks (Python 3.11+)."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import tomllib
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def validate(root: Path) -> None:
    root = root.resolve()
    manifest_path = root / 'package-manifest.json'
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    listed = data['files']
    actual = {
        p.relative_to(root).as_posix() for p in root.rglob('*')
        if p.is_file() and not any(part in {'.git', '__pycache__', '.venv', 'dist'} for part in p.relative_to(root).parts)
        and p != manifest_path and not p.name.endswith(('.pyc', '.pyo'))
    }
    if actual != set(listed):
        raise ValueError(f'Inventory differs; missing={sorted(set(listed)-actual)}, unlisted={sorted(actual-set(listed))}')
    for name, expected in listed.items():
        path = root / name
        if not path.resolve().is_relative_to(root):
            raise ValueError(f'Path escaped package: {name}')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError(f'Hash mismatch: {name}')
        if path.suffix in {'.md', '.py', '.toml', '.yaml', '.yml', '.json', '.svg'}:
            text = raw.decode('utf-8')
            if path.suffix == '.md':
                for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
                    if link.startswith(('#', 'http:', 'https:', 'mailto:')):
                        continue
                    destination = (path.parent / link.split('#')[0]).resolve()
                    if not destination.is_relative_to(root) or not destination.exists():
                        raise ValueError(f'Broken local link in {name}: {link}')
            if path.suffix == '.toml':
                tomllib.loads(text)
            if path.suffix == '.json':
                json.loads(text)
            if path.suffix == '.svg':
                ET.fromstring(text)
    entry = (root / 'council/SKILL.md').read_text(encoding='utf-8')
    if not entry.startswith('---\nname: council\n'):
        raise ValueError('Council skill frontmatter missing')
    profiles = {
        'council-sol.toml': ('council_sol', 'gpt-6.1-sol'),
        'council-astra.toml': ('council_astra', 'gpt-6-astra'),
        'council-luna.toml': ('council_luna', 'gpt-6-luna'),
    }
    if {p.name for p in (root / 'council/assets').glob('*.toml')} != set(profiles):
        raise ValueError('Council agent profile inventory differs')
    for filename, (name, model) in profiles.items():
        profile = tomllib.loads((root / 'council/assets' / filename).read_text(encoding='utf-8'))
        if profile.get('name') != name or profile.get('model') != model or profile.get('model_reasoning_effort') != 'max':
            raise ValueError(f'Council profile does not match the fixed contract: {filename}')
    spec = importlib.util.spec_from_file_location('council_check_run', root / 'council/scripts/check_run.py')
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    assignments = runtime.contract(root / 'council/SKILL.md')
    role_agents = {'Strategist': 'council_sol', 'Skeptic': 'council_astra',
                   'Creative': 'council_astra', 'Operator': 'council_sol',
                   'Audience Advocate': 'council_luna', 'Synthesizer': 'council_sol'}
    for role, assignment in assignments.items():
        if assignment['agent'] != role_agents[role]:
            raise ValueError(f'Role/profile assignment differs for {role}')
        filename = assignment['agent'].replace('_', '-') + '.toml'
        if filename not in profiles:
            raise ValueError(f'Unknown Council agent type for {role}')
        profile = tomllib.loads((root / 'council/assets' / filename).read_text(encoding='utf-8'))
        if assignment['model'] != profile['model'] or assignment['effort'] != profile['model_reasoning_effort']:
            raise ValueError(f'Model table/profile mismatch for {role}')
    asset = root / 'docs/images/assets/openai.svg'
    assets = json.loads((root / 'docs/images/logo-assets.json').read_text(encoding='utf-8'))
    for record in assets.values():
        if hashlib.sha256(asset.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('Logo asset hash differs from provenance')
    print(f'Package verified: {len(actual)} files, hashes, local links, JSON/TOML/SVG, three Council model profiles.')
    print('Installation checks only; runtime completion uses council/scripts/check_run.py. Neither proves decision quality.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path, default=ROOT)
    validate(parser.parse_args().root)
