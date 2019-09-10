import json

from django.forms import (modelform_factory, ModelForm)
from app.widgets import CodeEditor
from .models import (GuideEmailCampaign)

class GuideEmailCampaignForm(ModelForm):
    class Meta:
        fields = '__all__'
        labels = {
            'data':'HTML/YAML Override'
        }
        widgets = {
            'data': CodeEditor(attrs={'data-mode':'yaml', 'style': 'width: 90%; height: 100%;'}),
        }

    def __init__(self, *args, **kwargs):
        inst = kwargs.get("instance", None)
        super().__init__(*args, **kwargs)
        self.fields['data'].widget = CodeEditor(
            attrs={
            'data-mode':'yaml',
            'style':'width: 90%; height: 100%;'
        })
