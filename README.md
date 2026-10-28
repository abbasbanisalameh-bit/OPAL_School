## OPAL Update 131.7 R157 — الحزمة الموحدة

يجمع إصلاحات R157 وR158 في حزمة واحدة، مع توحيد هوية الإصدار إلى `131.7` ورقم مراجعة `157`. راجع `INSTALL_OPAL_UPDATE_131_7_R157_AR.md`.

# OPAL ERP — Update 130.0

حزمة تثبيت كاملة تجمع تحديثات 128–129.2 مع إصلاحات الاستقرار المطلوبة للاعتماد الفعلي.

- عرض جميع الجداول كمصفوفة أفقية موحّدة: اليوم مرة واحدة في اليمين والحصص أفقيًا.
- تمييز صف اليوم والحصة الجارية لحظيًا وفق اليوم ووقت بداية الحصة ونهايتها.
- منع تمدد الصفحة أفقيًا على الهاتف، وتثبيت القائمة الجانبية داخل حدود الشاشة.
- إصلاح ترتيب هجرات القبول والوثائق كي ينجح إنشاء قاعدة جديدة أو ترقية قاعدة قائمة.
- تثبيت أمان قاعدة SQLite قبل تطبيق التحديث، وتحسين استعلامات لوحة القيادة.
- تصحيح عقود الحضور وملف الطالب 360 وإنهاء المعلم ومؤشر TPI واختبارات البوابات.
- لا تتضمن الحزمة قاعدة بيانات أو ملفات وسائط أو أسرار بيئة، ولا تمس البيانات التشغيلية.

راجع `OPAL_UPDATE_130_PRODUCTION_STABILITY_RELEASE_NOTES_AR.md` للتفاصيل،
و`INSTALL_OPAL_UPDATE_130_PRODUCTION_STABILITY_AR.md` لطريقة التثبيت.


## R39 Transport Fixes
- Driver templates use the canonical base/base.html.
- Driver credential redirect uses transport:driver-credentials.
- Transport center owns the route-management UI while persisting the canonical admissions.TransportRoute records.
- Duplicate trip/driver action blocks and duplicate URL patterns were removed from the transport package.


## OPAL Update 131.7 R157
Restores the existing login/account UI, removes duplicated profile logout markup, and relocates the existing timetable matrix/live-events display to a canonical overview route linked from timetable navigation and quick access. See `INSTALL_OPAL_UPDATE_131_7_R157_AR.md`.

## OPAL Update 131.7 R159 — شاشة الجدول الموحدة

يدمج R159 الجدول الأسبوعي ومصفوفة الجدول الرسمية والأحداث الجارية والمنشئ الذكي في `templates/timetable/dashboard.html` الموجود، ويزيل قالب العرض المنفصل. يبقى اسم المسار القديم `timetable:overview` للتوافق فقط، ويعيد التوجيه إلى شاشة الجدول الموحدة. أزيل المدخل المكرر من قائمة الإدارة والوصول السريع؛ لا توجد نماذج بيانات أو ترحيلات جديدة.

راجع `INSTALL_OPAL_UPDATE_131_7_R159_AR.md` قبل التثبيت، و`OPAL_UPDATE_131_7_R159_VALIDATION_REPORT_AR.md` لنتائج الفحوص وحدودها.

## آخر تحديث
OPAL Update 131.7 R160 — Demo Data Reset Safety and Audit Log Preservation. راجع `OPAL_UPDATE_131_7_R160_RELEASE_NOTES_AR.md` وتعليمات التثبيت.
