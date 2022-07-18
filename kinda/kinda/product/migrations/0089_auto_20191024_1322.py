# Generated by Django 2.1.5 on 2019-10-24 10:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0088_product_shop'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shop_products', to='shop.Shop'),
        ),
    ]
