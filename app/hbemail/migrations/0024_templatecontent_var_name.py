# Generated by Django 2.2.4 on 2019-08-22 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hbemail', '0023_auto_20190822_1818'),
    ]

    operations = [
        migrations.AddField(
            model_name='templatecontent',
            name='var_name',
            field=models.CharField(default='body', max_length=255),
            preserve_default=False,
        ),
    ]