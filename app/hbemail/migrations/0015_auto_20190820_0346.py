# Generated by Django 2.2.4 on 2019-08-20 03:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hbemail', '0014_auto_20190820_0008'),
    ]

    operations = [
        migrations.RenameField(
            model_name='content',
            old_name='html',
            new_name='data',
        ),
    ]
