"""Install the complete Council folder; preserve existing files and config."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import sys
import tomllib
import uuid

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'council'
REQUIRED = (
    'SKILL.md', 'agents/openai.yaml', 'assets/luna-worker.toml',
    'references/council-recipes.md', 'references/council-evaluation.md',
)


def linked(path: Path) -> bool:
    return path.is_symlink() or getattr(path, 'is_junction', lambda: False)()


def install(dest: Path, *, replace: bool = False, agent_dir: Path | None = None) -> Path:
    from validate_package import validate
    validate(ROOT)
    dest = dest.expanduser().resolve()
    target = dest / 'council'
    if linked(target) or target.resolve().parent != dest:
        raise ValueError('Council target must be a direct, non-linked child of the destination')
    agent_target = None
    if agent_dir is not None:
        agent_dir = agent_dir.expanduser().resolve()
        agent_target = agent_dir / 'luna-worker.toml'
        if linked(agent_target):
            raise ValueError('Refusing a linked agent destination')
        for existing in agent_dir.glob('*.toml'):
            profile = tomllib.loads(existing.read_text(encoding='utf-8'))
            if profile.get('name') == 'luna_worker':
                if existing == agent_target and existing.read_bytes() == (SOURCE / 'assets/luna-worker.toml').read_bytes():
                    continue
                raise FileExistsError(f'luna_worker already exists: {existing}; compare it manually')
        if agent_target.exists() and agent_target.read_bytes() != (SOURCE / 'assets/luna-worker.toml').read_bytes():
            raise FileExistsError(f'Agent file exists: {agent_target}; it will not be overwritten')

    identical = target.is_dir() and {
        p.relative_to(target).as_posix(): p.read_bytes()
        for p in target.rglob('*') if p.is_file()
    } == {
        p.relative_to(SOURCE).as_posix(): p.read_bytes()
        for p in SOURCE.rglob('*') if p.is_file()
    }
    if target.exists() and not identical and not replace:
        raise FileExistsError(f'{target} already exists. Review it or use --replace to keep a backup and update')
    if not identical:
        dest.mkdir(parents=True, exist_ok=True)
        stage = dest / f'.council-stage-{uuid.uuid4().hex[:8]}'
        shutil.copytree(SOURCE, stage)
        backup = None
        if target.exists():
            backup = dest / f'council.backup-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:8]}'
            if target.resolve().parent != dest or backup.parent != dest:
                raise ValueError('Replacement paths escaped destination')
            target.rename(backup)
            print(f'Backup: {backup}')
        try:
            stage.rename(target)
        except OSError:
            if backup is not None and not target.exists():
                backup.rename(target)
            raise
    for name in REQUIRED:
        if (target / name).read_bytes() != (SOURCE / name).read_bytes():
            raise ValueError(f'Installed file mismatch: {name}')
    if agent_target is not None:
        agent_target.parent.mkdir(parents=True, exist_ok=True)
        if not agent_target.exists():
            shutil.copy2(SOURCE / 'assets/luna-worker.toml', agent_target)
        print(f'Agent profile: {agent_target}')
    print(f'Council installed and verified: {target}')
    print('Open a fresh Codex chat and invoke $council. Model access is not granted by installation.')
    print('Existing config.toml and permission settings were not modified.')
    return target


def main() -> int:
    codex_home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', type=Path, default=codex_home / 'skills', help='Parent skill directory')
    parser.add_argument('--replace', action='store_true', help='Back up a differing Council before updating')
    parser.add_argument('--with-agent', action='store_true', help='Also install the standalone Luna profile')
    parser.add_argument('--agent-dir', type=Path, default=codex_home / 'agents')
    args = parser.parse_args()
    try:
        install(args.dest, replace=args.replace, agent_dir=args.agent_dir if args.with_agent else None)
    except (ValueError, OSError, tomllib.TOMLDecodeError) as exc:
        print(f'Installation stopped: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
