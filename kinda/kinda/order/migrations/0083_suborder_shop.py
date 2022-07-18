# Generated by Django 2.1.5 on 2019-10-25 11:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0020_auto_20191014_1829'),
        ('order', '0082_auto_20191024_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='suborder',
            name='shop',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shop_orders', to='shop.Shop'),
        ),
    ]