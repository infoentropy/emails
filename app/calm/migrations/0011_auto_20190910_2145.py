# Generated by Django 2.2.4 on 2019-09-10 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iterablegen', '0008_iterablecampaign_campaignid'),
        ('calm', '0010_auto_20190910_2056'),
    ]

    operations = [
        migrations.AddField(
            model_name='guideemailcampaign',
            name='iterable_campaign_id',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='guideemailcampaign',
            name='iterablegen_campaign',
            field=models.ForeignKey(blank=True, null=True, on_delete=None, to='iterablegen.IterableCampaign'),
        ),
        migrations.AlterField(
            model_name='guideemailcampaign',
            name='format',
            field=models.CharField(blank=True, choices=[('htmlmixed', 'html'), ('javascript', 'js'), ('markdown', 'markdown')], default='yaml', max_length=32, null=True),
        ),
    ]
