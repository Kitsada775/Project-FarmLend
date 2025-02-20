# Generated by Django 5.1.1 on 2024-12-15 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0006_schedule_time"),
    ]

    operations = [
        migrations.AddField(
            model_name="car",
            name="status",
            field=models.CharField(
                choices=[("Pending", "Pending"), ("Approved", "Approved")],
                default="Pending",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="schedule",
            name="time",
            field=models.CharField(
                choices=[("morning", "ช่วงเช้า"), ("afternoon", "ช่วงบ่าย")],
                default=0,
                max_length=20,
            ),
        ),
    ]
