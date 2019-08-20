# Generated by Django 2.2.4 on 2019-08-19 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hbemail', '0010_templateregion_html'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComponentSchema',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
