# Generated by Django 2.1.5 on 2019-08-30 08:43

from django.db import migrations
import django_prices.models
import saleor.core.utils.taxes


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0073_suborder_subtotal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suborder',
            name='subtotal',
            field=django_prices.models.MoneyField(currency='USD', decimal_places=2, default=saleor.core.utils.taxes.zero_money, max_digits=12),
        ),
    ]
