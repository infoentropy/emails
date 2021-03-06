# Generated by Django 2.2.4 on 2019-09-05 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iterablegen', '0003_iterablecampaignsnippet_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='IterableCampaignCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
