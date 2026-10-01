from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parent.parent


def source(path):
    return (ROOT / path).read_text(encoding="utf-8")


class Update1317R146StudentParentUIContract(unittest.TestCase):
    def test_manifest_revision_is_146(self):
        manifest = json.loads(source("OPAL_UPDATE_MANIFEST.json"))
        self.assertEqual(manifest["package_revision"], 146)
        self.assertEqual(manifest["baseline"], "OPAL Update 131.7 R145 - Global Table Horizontal Scroll Authority")

    def test_marks_matrix_contracts_exist(self):
        student = source("templates/students/student_360.html")
        parent = source("templates/parent_portal/marks.html")
        for text in ("الامتحان الأول /20", "الامتحان الثاني /20", "الامتحان الثالث /20", "الامتحان النهائي /40", "المجموع /100"):
            self.assertIn(text, student)
            self.assertIn(text, parent)
        self.assertIn("student_rank", source("students/student360.py"))
        self.assertIn("subject_style row.subject", student)

    def test_parent_attendance_and_notes_contracts(self):
        attendance = source("templates/parent_portal/attendance.html")
        notes = source("templates/parent_portal/notes.html")
        dashboard = source("templates/parent_portal/dashboard.html")
        for text in ("غياب", "مغادرات", "وقت المغادرة", "التفاصيل"):
            self.assertIn(text, attendance)
        for text in ("الإدارة", "مربي الصف", "معلم", "ملاحظة"):
            self.assertIn(text, notes)
        self.assertIn("parent_portal:notes", dashboard)
        self.assertNotIn("parent_portal:teacher_evaluations", dashboard)

    def test_student_note_permissions_have_separate_roles(self):
        model = source("students/models.py")
        teacher_views = source("teachers/views.py")
        self.assertIn('("management", "ملاحظة الإدارة")', model)
        self.assertIn('("homeroom", "ملاحظة مربي الصف")', model)
        self.assertIn('("subject", "ملاحظة معلم المادة")', model)
        self.assertIn("assignment.section.homeroom_teacher_id != teacher.pk", teacher_views)

    def test_global_instant_table_search_has_no_30_row_gate(self):
        js = source("static/js/opal_erp.js")
        self.assertIn("table[data-opal-instant-table], table.opal-table, table.table", js)
        self.assertNotIn("bodyRows.length < 30", js)

    def test_live_event_matrix_is_section_horizontal(self):
        template = source("templates/timetable/dashboard.html")
        self.assertIn("opal-live-section-head", template)
        self.assertIn("opal-live-event-row", template)


if __name__ == "__main__":
    unittest.main()
