# OPAL R112 — تدقيق التكرار والتنقل

## منهج التدقيق
تم إجراء تدقيق ساكن لقوالب Django بحثًا عن تكرار مسارات البوابات الرئيسية، ثم مراجعة مواضع التكرار المعروفة في الإعدادات ولوحة الإدارة. التكرار داخل القوالب الداخلية الذي يمثل انتقالًا شرعيًا إلى تفاصيل الكيان لم يُحذف تلقائيًا.

## قرارات التصحيح
- إزالة رابط «إدارة الصفوف والشعب» المكرر من صفحة إعدادات النظام؛ تبقى الوظيفة في بوابة «الصفوف والشعب».
- تجميع مؤشرات لوحة الإدارة في مجموعات مالكة بدل عرضها كستة تطبيقات متجاورة.
- الإبقاء على الروابط التي تعمل كاختصار سياقي داخل الصفحة عندما تكون جزءًا من سير العمل ولا تنشئ بوابة بديلة.

## تكرار مسارات البوابات الرئيسية المكتشف ساكنًا
- **الرئيسية** — `dashboard:home`: 10 مواضع قالب.
  - `templates/403.html`
  - `templates/registration/password_change_form.html`
  - `templates/registration/password_change_done.html`
  - `templates/learning_platform/manager_dashboard.html`
  - `templates/learning_platform/base.html`
  - `templates/learning_platform/base.html`
  - `templates/base/base.html`
  - `templates/base/base.html`
  - `templates/core/system_settings.html`
  - `templates/enterprise_ops/dashboard.html`
- **منصة أوبال التعليمية** — `learning_platform:manager_dashboard`: 4 مواضع قالب.
  - `templates/learning_platform/_manager_nav.html`
  - `templates/learning_platform/base.html`
  - `templates/learning_platform/base.html`
  - `templates/learning_platform/base.html`
- **الطلبة** — `students:student_list`: 2 مواضع قالب.
  - `templates/students/student_form.html`
  - `templates/students/student_360.html`
- **المعلمين** — `teachers:dashboard`: 1 مواضع قالب.
  - `templates/timetable/dashboard.html`
- **أولياء الأمور** — `parent_portal:family_management`: 1 مواضع قالب.
  - `templates/parent_portal/family_detail.html`
- **الصفوف والشعب** — `academics:academic_structure`: 8 مواضع قالب.
  - `templates/admissions/registration_settings.html`
  - `templates/admissions/registration_settings.html`
  - `templates/admissions/direct_registration.html`
  - `templates/academics/academic_structure.html`
  - `templates/academics/academic_structure.html`
  - `templates/academics/academic_structure.html`
  - `templates/academics/academic_structure.html`
  - `templates/core/system_settings.html`
- **المواد الدراسية** — `academics:subject_list`: 1 مواضع قالب.
  - `templates/academics/subject_form.html`
- **الامتحانات** — `exams:exam_cycle_center`: 2 مواضع قالب.
  - `templates/exams/gradebook.html`
  - `templates/academics/academic_year_close.html`
- **الجدول الأسبوعي** — `timetable:dashboard`: 1 مواضع قالب.
  - `templates/timetable/form.html`
- **المالية** — `accounting:dashboard`: 0 مواضع قالب.
- **المواصلات** — `transport:transport-dashboard`: 1 مواضع قالب.
  - `templates/core/system_settings.html`
- **الوثائق** — `documents:document_list`: 3 مواضع قالب.
  - `templates/documents/template_list.html`
  - `templates/documents/settings.html`
  - `templates/documents/document_detail.html`
- **إعدادات النظام** — `core:system_settings`: 1 مواضع قالب.
  - `templates/core/production_reset_report.html`
- **الملف الشخصي** — `accounts:my_profile`: 2 مواضع قالب.
  - `templates/includes/topbar.html`
  - `templates/includes/sidebar.html`

## ملاحظة
عدد مرات ظهور URL في القوالب لا يعني تلقائيًا تكرار وظيفة؛ فبعضها breadcrumbs أو أزرار رجوع أو روابط سياقية داخل نفس سير العمل. لذلك اقتصر الحذف على التكرارات التي ثبت أنها في غير موضعها.
