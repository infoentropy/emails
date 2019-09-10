import json
import logging
logger = logging.getLogger(__name__)

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from app.widgets import CodeEditor
from .models import (
    Program,
    Guide,
    GuideEmailCampaign
)
from .serializers import (
    ProgramSerializer,
    GuideSerializer,
    GuideEmailCampaignSerializer)
from .forms import (
    GuideEmailCampaignForm
)
from .utils import CalmAPI

CALM_API_CLIENT = CalmAPI()


class GuideInlineAdmin(admin.TabularInline):
    model = Guide
    extra = 0

class GuideEmailCampaignInlineAdmin(admin.StackedInline):
    model = GuideEmailCampaign
    extra = 1

class ProgramAdmin(admin.ModelAdmin):
    model = Program
    inlines = [GuideInlineAdmin]
    # readonly_fields = ['import_program_link', ]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('<int:id>/import',
            self.admin_site.admin_view(self.import_program_view),
            name='admin_import'),
        ]
        return my_urls + urls


    def import_program_view(self, request, id):
        context = dict(self.admin_site.each_context(request))
        program = self.model.objects.get(pk=id)
        data = program.fetch()
        updated = program.sync(ProgramSerializer, data=data)

        # check and update child guides.
        if updated.is_valid():
            for g in data['guides']:
                guide_data = Guide.translate_api_for_serializer(None, g)
                try:
                    guide = Guide.objects.get(guide_id=g['guide_id'])
                    guide.sync(GuideSerializer, data=guide_data)
                except:
                    del g['id']
                    g['program'] = id
                    guide = GuideSerializer(data=guide_data)
                    if guide.is_valid():
                        g = guide.save()
                        logger.debug("saved guide", g)
                    else:
                        raise
        return HttpResponse(updated.errors or updated)




class GuideAdmin(admin.ModelAdmin):
    model = Guide
    list_display = ['title', 'deeplink', 'parent_title']

    inlines = [GuideEmailCampaignInlineAdmin]

class GuideEmailCampaignAdmin(admin.ModelAdmin):
    model = GuideEmailCampaign

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'program':
            kwargs['queryset'] = Program.objects.sort('title', 'order')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = GuideEmailCampaignForm
        return super().get_form(request, obj, **kwargs)

admin.site.register(Program, ProgramAdmin)
admin.site.register(Guide, GuideAdmin)
admin.site.register(GuideEmailCampaign, GuideEmailCampaignAdmin)
