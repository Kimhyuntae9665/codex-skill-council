import contextlib
import io
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from install import AGENT_PROFILES, SOURCE, install
from validate_package import ROOT, validate


class InstallationTests(unittest.TestCase):
    def call(self, dest, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return install(dest, **kwargs)

    def test_clean_install_copies_every_skill_file_and_agent(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            target = self.call(base / 'skills', agent_dir=base / 'agents')
            expected = {p.relative_to(SOURCE): p.read_bytes() for p in SOURCE.rglob('*') if p.is_file()}
            actual = {p.relative_to(target): p.read_bytes() for p in target.rglob('*') if p.is_file()}
            self.assertEqual(expected, actual)
            self.assertEqual({p.name for p in (base / 'agents').glob('*.toml')}, set(AGENT_PROFILES))
            for filename in AGENT_PROFILES:
                self.assertEqual((base / 'agents' / filename).read_bytes(), (SOURCE / 'assets' / filename).read_bytes())

    def test_conflicting_skill_preserved_and_replace_backs_it_up(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            target = base / 'skills/council'
            target.mkdir(parents=True)
            (target / 'personal-note.txt').write_text('keep me', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                self.call(base / 'skills')
            self.assertEqual((target / 'personal-note.txt').read_text(), 'keep me')
            self.call(base / 'skills', replace=True)
            backup = list((base / 'skill-backups').glob('council.backup-*'))
            self.assertEqual(len(backup), 1)
            self.assertEqual((backup[0] / 'personal-note.txt').read_text(), 'keep me')
            self.assertFalse(backup[0].is_relative_to(base / 'skills'))
            self.assertEqual(list((base / 'skills').glob('council.backup-*')), [])

    def test_agent_collision_is_checked_before_skill_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            agents = base / 'agents'
            agents.mkdir()
            (agents / 'custom.toml').write_text('name = "council_luna"\nmodel = "personal-model"\n', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                self.call(base / 'skills', agent_dir=agents)
            self.assertFalse((base / 'skills/council').exists())
            self.assertEqual({p.name for p in agents.iterdir()}, {'custom.toml'})

    def test_differing_agent_file_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            agents = base / 'agents'
            agents.mkdir()
            original = 'name = "my_personal_astra"\nmodel = "personal-model"\n'
            (agents / 'council-astra.toml').write_text(original, encoding='utf-8')
            with self.assertRaises(FileExistsError):
                self.call(base / 'skills', agent_dir=agents)
            self.assertFalse((base / 'skills/council').exists())
            self.assertFalse((agents / 'council-sol.toml').exists())
            self.assertEqual((agents / 'council-astra.toml').read_text(), original)

    def test_upgrade_preserves_legacy_agent_and_backs_up_legacy_skill(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            old = base / 'skills/council/assets'
            old.mkdir(parents=True)
            legacy = b'name = "luna_worker"\nmodel = "gpt-5.6-luna"\n'
            (old / 'luna-worker.toml').write_bytes(legacy)
            agents = base / 'agents'
            agents.mkdir()
            (agents / 'luna-worker.toml').write_bytes(legacy)
            target = self.call(base / 'skills', replace=True, agent_dir=agents)
            self.assertFalse((target / 'assets/luna-worker.toml').exists())
            self.assertEqual((agents / 'luna-worker.toml').read_bytes(), legacy)
            backup = next((base / 'skill-backups').glob('council.backup-*'))
            self.assertEqual((backup / 'assets/luna-worker.toml').read_bytes(), legacy)
            for filename in AGENT_PROFILES:
                self.assertEqual((agents / filename).read_bytes(), (SOURCE / 'assets' / filename).read_bytes())

    def test_identical_agent_reinstall_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            self.call(base / 'skills', agent_dir=base / 'agents')
            self.call(base / 'skills', agent_dir=base / 'agents')
            self.assertEqual(list((base / 'skills').glob('council.backup-*')), [])
            self.assertEqual({p.name for p in (base / 'agents').glob('*.toml')}, set(AGENT_PROFILES))

    def test_identical_reinstall_is_idempotent_and_does_not_touch_config(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            config = base / 'config.toml'
            config.write_text('model = "my-current-model"\n', encoding='utf-8')
            self.call(base / 'skills')
            self.call(base / 'skills')
            self.assertEqual(config.read_text(), 'model = "my-current-model"\n')
            self.assertEqual(list((base / 'skills').glob('council.backup-*')), [])

    def test_package_manifest_matches_all_files(self):
        with contextlib.redirect_stdout(io.StringIO()):
            validate(ROOT)

    def test_missing_evaluation_reference_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            package = Path(temp) / 'package'
            shutil.copytree(ROOT, package, ignore=shutil.ignore_patterns('.git', '__pycache__', 'dist'))
            (package / 'council/references/council-evaluation.md').unlink()
            with self.assertRaisesRegex(ValueError, 'Inventory differs'):
                validate(package)


if __name__ == '__main__':
    unittest.main()
