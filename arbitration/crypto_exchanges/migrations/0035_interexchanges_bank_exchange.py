# Generated by Django 3.2.14 on 2022-10-25 16:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banks', '0015_alter_banksexchangeratesupdates_bank'),
        ('crypto_exchanges', '0034_p2pcryptoexchangesrates_intra_crypto_exchange'),
    ]

    operations = [
        migrations.AddField(
            model_name='interexchanges',
            name='bank_exchange',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bank_rate_inter_exchanges', to='banks.banksexchangerates'),
        ),
    ]
