from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0015_systemmobileapitoken")]

    operations = [
        migrations.AddField(
            model_name="school",
            name="dashboard_image",
            field=models.ImageField(blank=True, null=True, upload_to="school_dashboard/", verbose_name="صورة لوحة الرئيسية"),
        ),
        migrations.AddField(
            model_name="school",
            name="dashboard_image_position",
            field=models.CharField(
                choices=[
                    ("100% 0%", "أعلى اليمين"), ("50% 0%", "أعلى الوسط"), ("0% 0%", "أعلى اليسار"),
                    ("100% 50%", "الوسط يمين"), ("50% 50%", "الوسط"), ("0% 50%", "الوسط يسار"),
                    ("100% 100%", "أسفل اليمين"), ("50% 100%", "أسفل الوسط"), ("0% 100%", "أسفل اليسار"),
                ],
                default="50% 50%", max_length=32, verbose_name="موضع صورة لوحة الرئيسية",
            ),
        ),
    ]
