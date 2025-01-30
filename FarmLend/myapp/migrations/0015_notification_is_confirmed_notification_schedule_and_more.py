# Generated by Django 5.1.1 on 2025-01-29 05:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0014_notification"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="is_confirmed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="notification",
            name="schedule",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="myapp.schedule",
            ),
        ),
        migrations.AlterField(
            model_name="schedule",
            name="time",
            field=models.CharField(
                choices=[("morning", "ช่วงเช้า"), ("afternoon", "ช่วงบ่าย")],
                max_length=20,
            ),
        ),
    ]
