# Generated by Django 3.1.4 on 2021-03-20 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0003_statictarget_last_reset_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='remaining_traffic',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
