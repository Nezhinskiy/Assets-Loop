# Generated by Django 3.2.14 on 2022-09-15 11:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crypto_exchanges', '0008_auto_20220915_1526'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listsfiatcrypto',
            old_name='list_fiat',
            new_name='list_fiat_crypto',
        ),
        migrations.RemoveField(
            model_name='listsfiatcrypto',
            name='asset',
        ),
    ]