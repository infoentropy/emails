# Generated by Django 2.2.4 on 2019-08-17 19:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hbemail', '0004_auto_20190817_1643'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='template',
            name='base_template',
        ),
        migrations.AddField(
            model_name='template',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='hbemail.Template'),
        ),
    ]