# Generated by Django 2.2.4 on 2019-09-04 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hbemail', '0026_campaign_campaigncontent'),
    ]

    operations = [
        migrations.AddField(
            model_name='component',
            name='data_type',
            field=models.CharField(choices=[('markdown', 'Markdown'), ('yaml', 'YAML'), ('mjml', 'MJML'), ('htmlmixed', 'HTML'), ('iterable', 'Iterable')], default='markdown', max_length=64),
        ),
        migrations.AlterField(
            model_name='content',
            name='data_type',
            field=models.CharField(choices=[('markdown', 'Markdown'), ('yaml', 'YAML'), ('mjml', 'MJML'), ('htmlmixed', 'HTML'), ('iterable', 'Iterable')], default='markdown', max_length=64),
        ),
    ]
