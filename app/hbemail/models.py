from django.db import models
from jinja2 import (Template as JinjaTemplate)

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

    def load_template(self):
        def temp(x = None):
            return True
        return (self.html, self.name, temp)

    def render(self, environment):
        if self.parent:
            self.parent.load_template()
        tmpl = environment.get_template(self.name)
        return tmpl.render(tmpl = self)

class Region(MetadataMixin):
    pass

class TemplateRegion(models.Model):
    order = models.PositiveSmallIntegerField(default=0)
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    html = models.TextField(blank=True)

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

class Module(MetadataMixin):
    # Narrator Header
    components = models.ManyToManyField(Component, through='ModuleComponent')

class ModuleComponent(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    component = models.ForeignKey(Component, on_delete=models.CASCADE)

class Content(MetadataMixin):
    # HEADER with data inside
    component = models.ForeignKey('Component', on_delete=models.CASCADE)
    # content can extend other content
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    # json data?
    html = models.TextField()
