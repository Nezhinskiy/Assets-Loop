# Generated by Django 3.2.14 on 2022-10-26 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crypto_exchanges', '0036_auto_20221025_1859'),
    ]

    operations = [
        migrations.AddField(
            model_name='interexchanges',
            name='marginality_percentage',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='relatedmarginalitypercentages',
            name='marginality_percentage',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]