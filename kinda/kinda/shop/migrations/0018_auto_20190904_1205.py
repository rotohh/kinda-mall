# Generated by Django 2.1.5 on 2019-09-04 09:05

from django.db import migrations, models
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0017_auto_20190904_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='logo_alt',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='shop',
            name='logo',
            field=versatileimagefield.fields.VersatileImageField(blank=True, null=True, upload_to='logos'),
        ),
    ]