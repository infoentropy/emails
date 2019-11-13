import yaml
import mistune
import json

from datetime import datetime,timedelta
from django.db import models
from jinja2 import (
Template as JinjaTemplate,
Environment as JinjaEnvironment,
FunctionLoader,
)

iterableEnviron = JinjaEnvironment(
    variable_start_string="[[",
    variable_end_string="]]",
    loader=FunctionLoader(
        lambda tmpl_name: Component.objects.get(name=tmpl_name).load_template()
        ),
)

class MetadataMixin(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True

# Create your models here.
class IterableCampaignSnippet(models.Model):
    class Meta:
        ordering = ['campaign', 'order', ]

    campaign = models.ForeignKey('IterableCampaign', on_delete=models.CASCADE)
    snippet = models.ForeignKey('IterableSnippet', on_delete=models.CASCADE, related_name='snippets')
    guide = models.ForeignKey('calm.Guide', blank=True, null=True, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=0)
    data = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{} {} {}".format(self.campaign.name, self.snippet.name, self.order)

    def load_data(self):
        return yaml.safe_load(self.data) or {}

    def load_schema(self):
        if self.snippet.schema:
            return yaml.safe_load(self.snippet.schema)
        return {}

    @property
    def snippet_args(self):
        schema = self.load_schema()
        if schema:
            data = self.load_data()
            schema.update(data)
            snippety = ["%s=\"%s\"" % (key, val or '') for key,val in schema.items()]
            return "\n".join(snippety)
        return ''


class OrderedIterableCampaignSnippet(IterableCampaignSnippet):
    # https://docs.djangoproject.com/en/dev/topics/db/models/#proxy-models
    class Meta:
        proxy = True
        ordering = ['order', ]

class IterableSnippet(MetadataMixin):
    schema = models.TextField(blank=True, null=True)
    markup = models.TextField(blank=True, null=True)
    needsWrap = models.BooleanField(default=False)

class IterableCampaign(MetadataMixin):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published')
    ]
    subject = models.CharField(max_length=256)
    preheaderText = models.CharField(max_length=256)
    status = models.CharField(choices=STATUS_CHOICES, max_length=128, default='draft')
    category = models.ForeignKey('IterableCampaignCategory', on_delete=None, blank=True, null=True)
    campaignId = models.CharField(max_length=32, null=True, blank=True)
    snippets = models.ManyToManyField('IterableSnippet', through='IterableCampaignSnippet')

    def get_snippets(self):
        return self.snippets.order_by('snippets__order')

class IterableCampaignCategory(MetadataMixin):
    class Meta:
        verbose_name_plural = "IterableCampaignCategories"
