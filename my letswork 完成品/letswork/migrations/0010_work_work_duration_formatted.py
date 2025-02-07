# Generated by Django 4.2 on 2025-01-30 02:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('letswork', '0009_remove_work_work_duration_formatted'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='work_duration_formatted',
            field=models.CharField(blank=True, default='', max_length=10, verbose_name='労働時間（HH:MM形式）'),
        ),
    ]
