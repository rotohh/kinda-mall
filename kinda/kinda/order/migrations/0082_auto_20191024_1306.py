# Generated by Django 2.1.5 on 2019-10-24 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0081_suborder_shop_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentout',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('sent to seller', 'sent to seller')], default='pending', max_length=15),
        ),
        migrations.AlterField(
            model_name='suborder',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'pending'), ('sent to seller', 'sent to seller')], default='pending', max_length=15),
        ),
        migrations.AlterField(
            model_name='suborder',
            name='status',
            field=models.CharField(choices=[('canceled', 'Canceled'), ('pending', 'pending'), ('picked from seller', 'picked from seller')], default='pending', max_length=32),
        ),
    ]