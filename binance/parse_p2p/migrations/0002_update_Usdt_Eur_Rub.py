# Generated by Django 3.2.14 on 2022-07-14 21:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parse_p2p', '0001_add_Usdt_Eur_Rub'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usdteur',
            name='author',
        ),
        migrations.RemoveField(
            model_name='usdtrub',
            name='author',
        ),
    ]
