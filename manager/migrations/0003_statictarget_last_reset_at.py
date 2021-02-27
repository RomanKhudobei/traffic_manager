# Generated by Django 3.1.4 on 2021-02-27 16:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_statictarget_traffic'),
    ]

    operations = [
        migrations.AddField(
            model_name='statictarget',
            name='last_reset_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
