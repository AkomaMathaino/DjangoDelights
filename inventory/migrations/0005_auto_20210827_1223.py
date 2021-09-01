# Generated by Django 3.2.6 on 2021-08-27 19:23

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_alter_purchase_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='menu_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory.menuitem'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2021, 8, 27, 12, 23, 40, 974235)),
        ),
    ]
