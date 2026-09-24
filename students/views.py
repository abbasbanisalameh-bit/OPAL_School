from django.db.models import Q, Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from enterprise_ops.permissions import management_required
from .models import Student
from .forms import StudentForm
from .lifecycle import build_student_profile_context

from admissions.models import StudentRegistration
from admissions.services import active_school, current_academic_year
from admissions.financial_services import students_current_year_finance_snapshots

@management_required
def student_list(request):
    q = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    school = active_school()
    academic_year = current_academic_year(school)
    students = Student.objects.all().order_by("full_name")

    if q:
        students = students.filter(
            Q(full_name__icontains=q)
            | Q(student_number__icontains=q)
            | Q(phone__icontains=q)
            | Q(national_id__icontains=q)
            | Q(guardian_name__icontains=q)
        )

    if status_filter:
        students = students.filter(status=status_filter)

    students = list(
        students.prefetch_related(
            Prefetch(
                "registrations",
                queryset=StudentRegistration.objects.filter(academic_year=academic_year).select_related("academic_year", "grade", "section").order_by("-created_at", "-pk"),
                to_attr="current_registrations",
            )
        )
    )
    snapshots = students_current_year_finance_snapshots(students, academic_year=academic_year) if students else {}
    for student in students:
        registration = student.current_registrations[0] if getattr(student, "current_registrations", []) else None
        finance = snapshots.get(student.pk, {"total": 0, "paid": 0, "remaining": 0, "status": ""})
        student.registered_grade = registration.grade if registration else getattr(student, "grade", None)
        student.registered_section = registration.section if registration else getattr(student, "section", None)
        student.current_registration = registration
        student.finance_summary = finance

    return render(request, "students/student_list.html", {
        "students": students,
        "q": q,
        "status_filter": status_filter,
        "status_choices": Student.STATUS_CHOICES,
        "current_year": academic_year,
    })

@management_required
def student_detail(request, pk):
    # رابط متوافق مع الصفحات القديمة؛ بطاقة الطالب هي الملف الموحد.
    get_object_or_404(Student, pk=pk)
    return redirect("students:student_360", pk=pk)

@management_required
def student_create(request):
    # تم اعتماد نموذج التسجيل الذكي كنموذج التسجيل الوحيد في النظام.
    return redirect("admissions:direct_registration")

@management_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect("students:student_360", pk=student.pk)
    else:
        form = StudentForm(instance=student)
    return render(request, "students/student_form.html", {"form": form, "title": "تعديل طالب"})

@management_required
def student_archive(request, pk):
    student = get_object_or_404(Student, pk=pk)
    # Status changes must pass through the audited academic lifecycle service.
    return redirect("academics:lifecycle_action", student_id=student.pk)


@management_required
def student_360(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, "students/student_360.html", build_student_profile_context(student))


@management_required
def student_360_print(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, "students/student_360_print.html", build_student_profile_context(student))
