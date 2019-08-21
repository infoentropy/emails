import json

from django.forms import (modelform_factory, ModelForm)
from app.widgets import CodeEditor
from .models import (Content, Component)

class YamlContentForm(ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'data': CodeEditor(attrs={'data-mode':'yaml', 'style': 'width: 90%; height: 100%;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.component:
            self.initial['data'] = self.instance.component.schema


class MarkdownContentForm(ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'data': CodeEditor(attrs={'data-mode':'markdown', 'style': 'width: 90%; height: 100%;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.component:
            self.initial['data'] = self.instance.component.schema

YamlContentAdminForm = modelform_factory(Content, form=YamlContentForm)
MarkdownContentAdminForm = modelform_factory(Content, form=MarkdownContentForm)

# https://mrcoffee.io/blog/code-editor-django-admin
class ComponentAdminForm(ModelForm):
    model = Component
    class Meta:
        fields = '__all__'
        widgets = {
            'schema': CodeEditor(attrs={'data-mode':'yaml', 'style': 'width: 90%; height: 100%;'}),
            'markup': CodeEditor(attrs={'data-mode':'htmlmixed', 'style': 'width: 90%; height: 100%;'})
        }
