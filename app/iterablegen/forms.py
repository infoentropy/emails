import json

from django.forms import (modelform_factory, ModelForm)
from app.widgets import CodeEditor
from .models import (
    IterableCampaignSnippet,
    IterableSnippet,
    IterableCampaign,
)

class CampaignSnippetForm(ModelForm):
    model = IterableCampaignSnippet
    class Meta:
        fields = '__all__'
        widgets = {
            'data': CodeEditor(attrs={'data-mode':'yaml', 'style': 'width: 90%; height: 100%;'}),
        }

    def __init__(self, *args, **kwargs):
        inst = kwargs.get("instance", None)
        super().__init__(*args, **kwargs)
        # prepopulate the field with schema from the parent component
        if self.instance:
            self.initial['data'] = self.instance.data
            if self.instance and self.instance.id:
                self.initial['data'] = self.instance.data or self.instance.snippet.schema


class SnippetForm(ModelForm):
    model = IterableSnippet
    class Meta:
        fields = '__all__'
        widgets = {
            'schema': CodeEditor(attrs={'data-mode':'yaml', 'style': 'width: 90%; height: 100%;'}),
            'markup': CodeEditor(attrs={'data-mode':'handlebars', 'style': 'width: 90%; height: 100%;'})
        }
