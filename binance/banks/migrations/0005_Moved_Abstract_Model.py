# Generated by Django 3.2.14 on 2022-07-31 17:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banks', '0004_Update_Abstract_Bank_Model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tinkoffexchanges',
            name='update',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='datas', to='banks.tinkoffupdates'),
        ),
    ]
