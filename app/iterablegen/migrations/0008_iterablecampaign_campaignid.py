# Generated by Django 2.2.4 on 2019-09-06 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iterablegen', '0007_iterablesnippet_needswrap'),
    ]

    operations = [
        migrations.AddField(
            model_name='iterablecampaign',
            name='campaignId',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
