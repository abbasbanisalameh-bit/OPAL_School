from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
MIGRATIONS = ROOT / "students" / "migrations"


class Update1317R146MigrationGraphContract(unittest.TestCase):
    def test_student_notes_migration_is_after_existing_student_chain(self):
        self.assertFalse((MIGRATIONS / "0006_studentnote.py").exists())
        note = (MIGRATIONS / "0012_studentnote.py").read_text(encoding="utf-8")
        self.assertIn('(\"students\", \"0011_student_photo_size_limit\")', note)

    def test_photo_migration_converges_legacy_0006_branch(self):
        photo = (MIGRATIONS / "0011_student_photo_size_limit.py").read_text(encoding="utf-8")
        self.assertIn('(\"students\", \"0010_alter_student_is_demo\")', photo)
        self.assertIn('(\"students\", \"0006_update_student_photo_size_limit\")', photo)


if __name__ == "__main__":
    unittest.main()
