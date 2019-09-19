from django.contrib import admin
from django.utils.html import format_html
# from django.urls import reverse, path
# from rest_framework.reverse import reverse

from app.widgets import CodeEditor

from .models import (
    IterableCampaignSnippet,
    IterableSnippet,
    IterableCampaign,
    IterableCampaignCategory,
)
from .forms import (
    SnippetForm,
    CampaignSnippetForm
)

# INLINES
class CampaignSnippetInline(admin.TabularInline):
    ordering = ('order', )
    model = IterableCampaignSnippet
    form = CampaignSnippetForm
    extra = 0

class CampaignInline(admin.TabularInline):
    ordering = ('-updated', )
    model = IterableCampaign
    readonly_fields = ['name', 'subject']
    exclude = ['description', 'preheaderText']
    can_delete = False
    extra = 0

# MAIN ADMIN
class IterableCampaignAdmin(admin.ModelAdmin):
    model = IterableCampaign
    inlines = [CampaignSnippetInline]
    list_display = ['subject', 'name', 'status', 'updated']

class IterableSnippetAdmin(admin.ModelAdmin):
    model = IterableSnippet
    form = SnippetForm

class IterableCampaignSnippetAdmin(admin.ModelAdmin):
    model = IterableCampaignSnippet
    # readonly_fields = ('publishToIterable', )
    # def publishToIterable(self, obj):
    #     if obj and obj.id:
    #         url = reverse('publishTemplate', args=(obj.id, ))
    #         return format_html('<a href="{}">Publish</a>', url)
    #     else:
    #         return "Save first"
    # publishToIterable.allow_tags = True

class IterableCampaignCategoryAdmin(admin.ModelAdmin):
    model = IterableCampaignCategory
    inlines = [CampaignInline]


admin.site.register(IterableCampaign, IterableCampaignAdmin)
admin.site.register(IterableSnippet, IterableSnippetAdmin)
admin.site.register(IterableCampaignSnippet, IterableCampaignSnippetAdmin)
admin.site.register(IterableCampaignCategory, IterableCampaignCategoryAdmin)
