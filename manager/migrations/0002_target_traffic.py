# Generated by Django 3.1.4 on 2020-12-21 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='target',
            name='traffic',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
