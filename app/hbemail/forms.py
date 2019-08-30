import json

from django.forms import (modelform_factory, ModelForm)
from app.widgets import CodeEditor
from .models import (Content, Component, Template, TemplateContent)

class TemplateContentForm(ModelForm):
    class Meta:
        # fields = '__all__'
        fields = ('order', 'var_name', 'content', 'data')
        labels = {
            'var_name':"Assign to Variable",
            'data':'HTML/YAML Override'
        }
        widgets = {
            'data': CodeEditor(attrs={'data-mode':'htmlmixed', 'style': 'width: 90%; height: 100%;'}),
        }

    def __init__(self, *args, **kwargs):
        inst = kwargs.get("instance", None)
        super().__init__(*args, **kwargs)
        self.fields['data'].widget = CodeEditor(
            attrs={
            'data-mode':(inst and inst.content and inst.content.data_type) or 'htmlmixed',
            'style':'width: 90%; height: 100%;'
        })

class TemplateForm(ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'html': CodeEditor(attrs={'data-mode':'jinja2', 'style': 'width: 90%; height: 100%;'}),
        }


class ContentForm(ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'data': CodeEditor(attrs={'data-mode':'yaml', 'style': 'width: 90%; height: 100%;'}),
        }

    def __init__(self, *args, **kwargs):
        inst = kwargs.get("instance", None)
        super().__init__(*args, **kwargs)
        self.fields['data'].widget = CodeEditor(
            attrs={
            'data-mode':inst and inst.data_type or 'htmlmixed',
            'style':'width: 90%; height: 100%;'
        })
        # prepopulate the field with schema from the parent component
        if self.instance and self.instance.component:
            self.initial['data'] = self.instance.data or self.instance.component.schema

TemplateContentAdminForm = modelform_factory(TemplateContent, form=TemplateContentForm)
ContentAdminForm = modelform_factory(Content, form=ContentForm)

# https://mrcoffee.io/blog/code-editor-django-admin
class ComponentAdminForm(ModelForm):
    model = Component
    class Meta:
        fields = '__all__'
        widgets = {
            'schema': CodeEditor(attrs={'data-mode':'yaml', 'style': 'width: 90%; height: 100%;'}),
            'markup': CodeEditor(attrs={'data-mode':'htmlmixed', 'style': 'width: 90%; height: 100%;'})
        }
