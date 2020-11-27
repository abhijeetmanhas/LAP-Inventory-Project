# Generated by Django 2.0.2 on 2020-11-27 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inv', '0012_auto_20201127_0846'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rental',
            name='returned',
        ),
        migrations.AddField(
            model_name='rental',
            name='requested',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='rental',
            name='approved',
            field=models.BooleanField(default=False),
        ),
    ]
