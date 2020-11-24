# Generated by Django 2.0.2 on 2020-11-23 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inv', '0005_remove_inventory_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='price',
            field=models.PositiveIntegerField(default=0.0),
            preserve_default=False,
        ),
    ]
