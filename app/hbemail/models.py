import yaml
import mistune
import json

from jinja2 import (
Template as JinjaTemplate,
)
from datetime import datetime,timedelta
from django.db import models
from .utils import send_to_iterable

RENDER_MARKDOWN = mistune.Markdown()

"""
Template
  Header
    content=[{block1}]
  Body
    content=[{ block1}, {block2}, {block3}]
  FOOTER
   content=[{ block1}, {block2}, {block3}]
"""
class MetadataMixin(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True

class BaseTemplate(MetadataMixin):
    pass

class Template(MetadataMixin):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey('TemplateCategory', on_delete=models.CASCADE, null=True, blank=True)
    html = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    subject = models.CharField(max_length=256)
    preheaderText = models.CharField(max_length=256)

    def load_template(self):
        def outdated(x = None):
            return self.updated > (datetime.now()-timedelta(seconds=1))
        return (self.html, self.name, outdated)

    def get_template(self, environment):
        if self.parent:
            self.parent.load_template()
        return environment.get_template(self.name)

    def publish(self, environment, **kwargs):
        # publish to iterable.
        payload = self.render(environment)
        return send_to_iterable(payload)

    def render(self, environment, **kwargs):
        tmpl = self.get_template(environment)
        regiondata = {}
        for r in self.templatecontent_set.all().order_by('var_name', 'order'):
            region = r.var_name
            temp = regiondata.setdefault(region, '')
            # print(r.data)
            regiondata[region] = temp + ((r.content and r.content._render_data(child_data=r.data)) or r.data)

        kwargs.update(regiondata)
        return tmpl.render(
            tmpl = self,
            **kwargs)

# class Region(MetadataMixin):
#     pass

class TemplateContent(models.Model):
    order = models.PositiveSmallIntegerField(default=0)
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    content = models.ForeignKey('Content', on_delete=models.CASCADE, null=True, blank=True)
    data = models.TextField(blank=True)
    # the var in which to inject the content
    var_name = models.CharField(max_length=255)
    # region = models.ForeignKey(Region, on_delete=models.CASCADE)

class TemplateCategory(MetadataMixin):
    class Meta:
        verbose_name_plural = "TemplateCategories"

class ComponentCategory(MetadataMixin):
    # Meta, Header, Body, Footer

    class Meta:
        verbose_name_plural = "ComponentCategories"

class ComponentSchema(MetadataMixin):
    pass

class Component(MetadataMixin):
    # it's a HEADER/BODY/FOOTER element
    category = models.ForeignKey('ComponentCategory', on_delete=models.CASCADE)
    schema = models.TextField(blank=True, null=True)
    markup = models.TextField(blank=True, null=True)

    def _pretty_json(self):
        try:
            return json.dumps(self.json, indent=2)
        except Exception as e:
            return (e)

    def _to_json(self):
        return yaml.safe_load(self.schema)

    json = property(_to_json)
    pretty_json = property(_pretty_json)

class Module(MetadataMixin):
    # Narrator Header
    components = models.ManyToManyField(Component, through='ModuleComponent')


class ModuleComponent(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)

class Campaign(MetadataMixin):
    pass

class Content(MetadataMixin):
    MARKDOWN = 'markdown'
    YAML = 'yaml'
    HTML = 'htmlmixed'
    DJANGO = 'django'
    MJML = 'mjml'

    CONTENT_CHOICES = [
        (MARKDOWN, 'Markdown'),
        (YAML, 'YAML'),
        (MJML, 'MJML'),
        (HTML, 'HTML')
    ]

    # Ex: HEADER component filled with data inside
    component = models.ForeignKey('Component', on_delete=models.CASCADE, blank=True, null=True)
    # content can extend other content?
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    data_type = models.CharField(max_length=64, choices=CONTENT_CHOICES, default=MARKDOWN)

    def _render_data(self, child_data=None):
        # not a component? it's freeform
        if self.data_type == self.MARKDOWN:
            try:
                return RENDER_MARKDOWN(child_data or self.data)
            except Exception as e:
                return "Markdown error: %s" % e
            return self.data
        elif self.component:
            try:
                schema = yaml.safe_load(self.component.schema)
                # override tmpl data with Content data
                schema.update(yaml.safe_load(self.data))
                # override tmpl data again with TemplateContent data
                if child_data:
                    child_data = yaml.safe_load(child_data)
                    schema.update(child_data)
                tmpl = JinjaTemplate(self.component.markup)
                return tmpl.render(schema)
            except Exception as e:
                return self.data
        else:
            return self.data

    preview = property(_render_data)
