# OPAL ERP — Production Baseline R130

## Baseline
- Release: `OPAL Update 131.7 R130 - Production Cleanup, Performance & Stable Baseline`
- Previous verified runtime release: R129 — Receipt Content Rendering Repair
- Version: `131.7`
- Branch target: `main`
- Official CSS authority: `static/css/opal_theme_system.css`

## Stable visual/functional surfaces confirmed before R130
- Themes: Light / Green / Dark
- Student 360
- Weekly timetable mobile containment
- Registration and fee receipts, including A4 landscape print
- Parent portal and parent account surfaces
- System settings

## R130 cleanup/performance changes
- Removed obsolete per-release installation/release-note files from the runtime source tree.
- Preserved executable regression contracts and architectural/system contract documents.
- Removed an accidental non-source terminal help artifact from the project root.
- Kept one CSS authority and cleaned historical CSS section commentary without changing successful visual rules.
- Global academic context resolution is read-only during ordinary page rendering.
- School live timetable status uses a 10-second process-local cache keyed by school/day/minute/guardian/section.
- Teacher portal reuses its already-calculated live status during the same request.
- Asset cache identity is advanced to the R130 production-cleanup token.

## Safety boundaries
R130 does not intentionally change database schema, migrations, financial data, permissions, URLs, enrollment/payment logic, or timetable data. No broad cache is applied to grades, attendance, finance, registration, or other transactional data.

## Required server acceptance
- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- `git diff --check`
- Runtime artifact audit
- `python manage.py audit_runtime_performance --iterations 3`
- Visual smoke test of the stable surfaces listed above

Only after these checks pass should the server tree be pushed as the clean `main` baseline to GitHub.
