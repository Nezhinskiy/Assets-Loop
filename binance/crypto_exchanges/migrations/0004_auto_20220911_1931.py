# Generated by Django 3.2.14 on 2022-09-11 15:31

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crypto_exchanges', '0003_interexchanges_interexchangesupdate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Card2CryptoExchangesUpdates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Update date')),
                ('duration', models.DurationField(default=datetime.timedelta(0))),
                ('crypto_exchange', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='card_2_crypto_exchanges_update', to='crypto_exchanges.cryptoexchanges')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Card2Fiat2CryptoExchangesUpdates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Update date')),
                ('duration', models.DurationField(default=datetime.timedelta(0))),
                ('crypto_exchange', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='card_2_fiat_2_crypto_exchanges_update', to='crypto_exchanges.cryptoexchanges')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='InterExchanges',
        ),
        migrations.DeleteModel(
            name='InterExchangesUpdate',
        ),
    ]
