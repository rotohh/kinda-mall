# Generated by Django 2.1.5 on 2019-06-17 12:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_auto_20190525_1135'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shopcategory',
            name='shop',
        ),
        migrations.DeleteModel(
            name='ShopCategory',
        ),
    ]
