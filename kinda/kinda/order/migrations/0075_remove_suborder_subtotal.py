# Generated by Django 2.1.5 on 2019-08-30 08:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0074_auto_20190830_1143'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='suborder',
            name='subtotal',
        ),
    ]
