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
AGENT_PROFILES = {
    'council-sol.toml': 'council_sol',
    'council-astra.toml': 'council_astra',
    'council-luna.toml': 'council_luna',
}
REQUIRED = (
    'SKILL.md', 'agents/openai.yaml',
    'references/council-recipes.md', 'references/council-evaluation.md',
    *(f'assets/{name}' for name in AGENT_PROFILES),
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
    agent_targets = []
    if agent_dir is not None:
        agent_dir = agent_dir.expanduser().resolve()
        for filename, name in AGENT_PROFILES.items():
            agent_target = agent_dir / filename
            if linked(agent_target):
                raise ValueError(f'Refusing a linked agent destination: {agent_target}')
            if agent_target.exists() and agent_target.read_bytes() != (SOURCE / 'assets' / filename).read_bytes():
                raise FileExistsError(f'Agent file exists: {agent_target}; it will not be overwritten')
            agent_targets.append(agent_target)
        for existing in agent_dir.glob('*.toml'):
            profile = tomllib.loads(existing.read_text(encoding='utf-8'))
            for filename, name in AGENT_PROFILES.items():
                if profile.get('name') == name:
                    if existing == agent_dir / filename and existing.read_bytes() == (SOURCE / 'assets' / filename).read_bytes():
                        continue
                    raise FileExistsError(f'{name} already exists: {existing}; compare it manually')

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
            backup_dir = dest.parent / 'skill-backups'
            if linked(backup_dir) or backup_dir.resolve().parent != dest.parent:
                raise ValueError('Backup directory must be a direct, non-linked sibling of the skill directory')
            backup_dir.mkdir(exist_ok=True)
            backup = backup_dir / f'council.backup-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:8]}'
            if target.resolve().parent != dest or backup.resolve().parent != backup_dir or backup.is_relative_to(dest):
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
    for agent_target in agent_targets:
        agent_target.parent.mkdir(parents=True, exist_ok=True)
        if not agent_target.exists():
            shutil.copy2(SOURCE / 'assets' / agent_target.name, agent_target)
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
    parser.add_argument('--with-agents', '--with-agent', dest='with_agents', action='store_true', help='Also install all three Council model profiles (--with-agent is a compatible alias)')
    parser.add_argument('--agent-dir', type=Path, default=codex_home / 'agents')
    args = parser.parse_args()
    try:
        install(args.dest, replace=args.replace, agent_dir=args.agent_dir if args.with_agents else None)
    except (ValueError, OSError, tomllib.TOMLDecodeError) as exc:
        print(f'Installation stopped: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
