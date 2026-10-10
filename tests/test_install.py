import contextlib
import io
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from install import SOURCE, install
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
            self.assertEqual((base / 'agents/luna-worker.toml').read_bytes(), (SOURCE / 'assets/luna-worker.toml').read_bytes())

    def test_conflicting_skill_preserved_and_replace_backs_it_up(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            target = base / 'council'
            target.mkdir()
            (target / 'personal-note.txt').write_text('keep me', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                self.call(base)
            self.assertEqual((target / 'personal-note.txt').read_text(), 'keep me')
            self.call(base, replace=True)
            backup = list(base.glob('council.backup-*'))
            self.assertEqual(len(backup), 1)
            self.assertEqual((backup[0] / 'personal-note.txt').read_text(), 'keep me')

    def test_agent_collision_is_checked_before_skill_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            agents = base / 'agents'
            agents.mkdir()
            (agents / 'custom.toml').write_text('name = "luna_worker"\nmodel = "personal-model"\n', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                self.call(base / 'skills', agent_dir=agents)
            self.assertFalse((base / 'skills/council').exists())

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
