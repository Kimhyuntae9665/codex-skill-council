"""Refresh the inventory after intentional package edits; review the diff before publishing."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'package-manifest.json'

if __name__ == '__main__':
    files = {}
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or path == OUT:
            continue
        relative = path.relative_to(ROOT)
        if any(part in {'.git', '__pycache__', '.venv', 'dist'} for part in relative.parts) or path.name.endswith(('.pyc', '.pyo')):
            continue
        files[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    OUT.write_text(json.dumps({'format': 1, 'version': '1.3.1', 'files': files}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    print(f'Inventory refreshed: {len(files)} files. Review changes before treating these hashes as a release.')
