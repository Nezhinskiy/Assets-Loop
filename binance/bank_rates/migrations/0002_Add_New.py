# Generated by Django 3.2.14 on 2022-08-05 16:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bank_rates', '0001_Add_New'),
    ]

    operations = [
        migrations.AddField(
            model_name='banksexchangeratesupdates',
            name='bank',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='bank_rates_update', to='bank_rates.banks'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='intrabanksexchangesupdates',
            name='bank',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='bank_exchanges_update', to='bank_rates.banks'),
            preserve_default=False,
        ),
    ]