# Generated by Django 4.2 on 2024-12-21 13:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('letswork', '0005_rename_a_id_paid_a_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='attendance_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
