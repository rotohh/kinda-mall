# Generated by Django 2.1.5 on 2019-10-24 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0004_auto_20191015_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentstemporary',
            name='order_payment_status',
            field=models.CharField(choices=[('pending', 'pending'), ('paid', 'paid')], default='pending', max_length=32),
        ),
        migrations.AlterField(
            model_name='paymentstemporary',
            name='shipping_payment_status',
            field=models.CharField(choices=[('pending', 'pending'), ('paid', 'paid')], default='pending', max_length=32),
        ),
    ]