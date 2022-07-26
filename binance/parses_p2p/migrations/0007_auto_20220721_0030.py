# Generated by Django 3.2.14 on 2022-07-20 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parses_p2p', '0006_remove_p2pbinance_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='p2pbinance',
            name='asset',
            field=models.CharField(choices=[('USDT', 'USDT'), ('BUSD', 'BUSD'), ('BTC', 'BTC'), ('ETH', 'ETH')], max_length=4),
        ),
        migrations.AlterField(
            model_name='p2pbinance',
            name='fiat',
            field=models.CharField(choices=[('RUB', 'rub'), ('USD', 'usd'), ('EUR', 'eur'), ('GBP', 'gbp')], max_length=3),
        ),
    ]
