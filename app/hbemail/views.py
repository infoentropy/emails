import mjml

from django.shortcuts import render
from django.http import HttpResponse
from jinja2 import (
BaseLoader,
Environment,
FunctionLoader,
Template as Jinja,
select_autoescape,
)

from app.widgets import MjmlExtension

from .models import (BaseTemplate,
Template,
TemplateCategory,
TemplateContent,
Module,
ModuleComponent,
Component,
ComponentCategory,
Content,
)

jinjaenv = Environment(
    extensions=[MjmlExtension],
    loader=FunctionLoader(
        lambda tmpl_name: Template.objects.get(name=tmpl_name).load_template()
        ),
)

# Create your views here.
def index(request):
    return HttpResponse("hello")

def templates(request):
    templates = Template.objects.all()
    template = Jinja('{% for a in templates %}<div>{{a.name}}</div>{% endfor %}')
    return HttpResponse(template.render(dict(templates=templates)))

def template(request, id):
    tmpl = Template.objects.get(pk=id)
    return HttpResponse(tmpl.render(jinjaenv))
