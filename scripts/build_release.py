"""Build a self-contained ZIP from the verified manifest; no network or publishing."""
import argparse
from pathlib import Path
import zipfile

from validate_package import ROOT, validate

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/codex-skill-council.zip')
    args = parser.parse_args()
    validate(ROOT)
    import json
    names = list(json.loads((ROOT / 'package-manifest.json').read_text(encoding='utf-8'))['files'])
    names.append('package-manifest.json')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(names):
            archive.write(ROOT / name, 'codex-skill-council/' + name)
    print(f'Release ZIP: {args.output.resolve()} ({len(names)} files)')
