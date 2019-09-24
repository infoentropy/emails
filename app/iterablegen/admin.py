import logging
from pudb import set_trace
logger = logging.getLogger(__name__)

from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.html import format_html
from django.urls import path,reverse
from django.contrib import (admin,messages)
# from rest_framework.reverse import reverse

from app.widgets import CodeEditor
from hbemail.utils import send_to_iterable
from .views import render_campaign
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
    fields = ['order', 'snippet', 'guide', 'data', ]
    ordering = ('order', )
    autocomplete_fields = ['snippet', 'guide']
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
    readonly_fields = ['somelink', 'exportlink']


    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('<int:id>/export',
            self.admin_site.admin_view(self.export),
            name='export'),
        ]
        return my_urls + urls

    def export(self, request, id):
        # set_trace()
        from .views import render_campaign
        campaign = self.model.objects.get(pk=id)
        payload = render_campaign(campaign)
        logger.debug(payload)
        response = send_to_iterable(
            templateId=int(campaign.campaignId),
            html=payload,
            subject=campaign.subject,
            preheaderText=campaign.preheaderText)
        logger.debug(response.content)
        if response.status_code == 200:
            messages.add_message(request, messages.INFO, "Exported to Iterable")
        else:
            messages.add_message(request, messages.ERROR, "FAILeD")
        return HttpResponseRedirect(reverse('admin:iterablegen_iterablecampaign_change', args=(id, )))

    def somelink(self, obj):
        if obj and obj.id:
            return format_html('<a href="{}?format=html" target="render">Show campaign</a>',
                        reverse('campaign-html', args=(obj.id,)))
        else:
            return "Save first"
    somelink.allow_tags = True

    def exportlink(self, obj):
        if obj and obj.id:
            return format_html('<a href="{}">Export Template</a>',
                        reverse('admin:export', args=(obj.id,)))
        else:
            return "Save first"
    exportlink.allow_tags = True

    def render(self, obj):
        return render_campaign(obj)

class IterableSnippetAdmin(admin.ModelAdmin):
    model = IterableSnippet
    form = SnippetForm
    search_fields = ['name', ]
    ordering = ('name', )

class IterableCampaignSnippetAdmin(admin.ModelAdmin):
    model = IterableCampaignSnippet
    list_display = ['campaign', 'snippet', 'order']

class IterableCampaignCategoryAdmin(admin.ModelAdmin):
    model = IterableCampaignCategory
    inlines = [CampaignInline]


admin.site.register(IterableCampaign, IterableCampaignAdmin)
admin.site.register(IterableSnippet, IterableSnippetAdmin)
admin.site.register(IterableCampaignSnippet, IterableCampaignSnippetAdmin)
admin.site.register(IterableCampaignCategory, IterableCampaignCategoryAdmin)
