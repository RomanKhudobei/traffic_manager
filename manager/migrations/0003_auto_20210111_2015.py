# Generated by Django 3.1.5 on 2021-01-11 20:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_target_traffic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='target',
            name='publish_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]