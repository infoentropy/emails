from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from app.widgets import CodeEditor

from .models import (
    IterableCampaignSnippet,
    IterableSnippet,
    IterableCampaign,
)
from .forms import (
    SnippetForm,
    CampaignSnippetForm
)

# INLINES
class CampaignSnippetInline(admin.StackedInline):
    ordering = ('order', )
    model = IterableCampaignSnippet
    form = CampaignSnippetForm
    extra = 0

# MAIN ADMIN
class IterableCampaignAdmin(admin.ModelAdmin):
    model = IterableCampaign
    inlines = [CampaignSnippetInline]

class IterableSnippetAdmin(admin.ModelAdmin):
    model = IterableSnippet
    form = SnippetForm

class IterableCampaignSnippetAdmin(admin.ModelAdmin):
    model = IterableCampaignSnippet

admin.site.register(IterableCampaign, IterableCampaignAdmin)
admin.site.register(IterableSnippet, IterableSnippetAdmin)
admin.site.register(IterableCampaignSnippet, IterableCampaignSnippetAdmin)
