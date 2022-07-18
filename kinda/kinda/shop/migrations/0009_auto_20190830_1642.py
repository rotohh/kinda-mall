# Generated by Django 2.1.5 on 2019-08-30 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_auto_20190617_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='shop',
            name='shop_link',
            field=models.URLField(blank=True, null=True),
        ),
    ]
