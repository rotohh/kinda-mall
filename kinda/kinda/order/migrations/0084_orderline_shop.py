# Generated by Django 2.1.5 on 2019-10-25 16:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0020_auto_20191014_1829'),
        ('order', '0083_suborder_shop'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderline',
            name='shop',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shop_order_lines', to='shop.Shop'),
        ),
    ]