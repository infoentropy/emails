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
    campaign = models.ForeignKey('IterableCampaign', on_delete=models.CASCADE)
    snippet = models.ForeignKey('IterableSnippet', on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(default=0)
    data = models.TextField(blank=True, null=True)


class IterableSnippet(MetadataMixin):
    schema = models.TextField(blank=True, null=True)
    markup = models.TextField(blank=True, null=True)

class IterableCampaign(MetadataMixin):
    subject = models.CharField(max_length=256)
    preheaderText = models.CharField(max_length=256)

    def openPreview(self, obj):
        if obj and obj.id:
            url = reverse('preview', args=(obj.id, ))
            return format_html('<a href="{}">Preview</a>', url)
        else:
            return "Save first"
    openPreview.allow_tags = True
