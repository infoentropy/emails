# Generated by Django 2.2.4 on 2019-08-20 22:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hbemail', '0018_template_regions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='template',
            name='regions',
        ),
    ]
