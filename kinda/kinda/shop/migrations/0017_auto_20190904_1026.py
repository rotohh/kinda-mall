# Generated by Django 2.1.5 on 2019-09-04 07:26

from django.db import migrations
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0016_auto_20190830_2344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='logo',
            field=versatileimagefield.fields.VersatileImageField(default='default.jpg', upload_to='logos'),
        ),
    ]