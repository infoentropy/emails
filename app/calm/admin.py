import json
import yaml
import logging

logger = logging.getLogger(__name__)

from jinja2 import Template

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from app.widgets import CodeEditor
from iterablegen.serializers import IterableCampaignSerializer
from rest_framework.renderers import JSONRenderer


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
    GuideEmailCampaignForm,
    GuideForm
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
    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = GuideForm
        return super().get_form(request, obj, **kwargs)

class GuideEmailCampaignAdmin(admin.ModelAdmin):
    model = GuideEmailCampaign

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('<int:id>/preview',
            self.admin_site.admin_view(self.preview),
            name='preview'),
            path('<int:id>/publicpreview',
            self.preview,
            name='preview'),
            path('<int:id>/snippet',
            self.admin_site.admin_view(self.snippet),
            name='snippet'),
        ]
        return my_urls + urls

    # this will hack the format into something that Iterable
    # can consume. A bit cludgy.
    def preview(self, request, id):
        obj = self.model.objects.get(pk=id)
        guide = obj.guide
        program = guide.program
        overrides = yaml.safe_load(obj.data)
        tmp = IterableCampaignSerializer(obj.iterablegen_campaign, context={'request':request})
        usabledata = json.loads(JSONRenderer().render(tmp.data))
        for idx, snippet in enumerate(usabledata['iterablecampaignsnippet_set']):
            orig = snippet['data']
            orig.update(overrides[idx])
            snippet['data'] = orig
            usabledata['iterablecampaignsnippet_set'][idx] = snippet
        temp = usabledata['iterablecampaignsnippet_set']
        usabledata['iterablecampaignsnippet_set']= {'list-item':temp}
        root = {"root":usabledata}
        t = Template(json.dumps(root))
        nextguide = None
        if program.meditation_type == 'sequential':
            currentPosition = int(guide.position)
            nextPosition = currentPosition+1
            try:
                nextguide = program.guide_set.get(position=nextPosition)
            except:
                logger.info("position %s not here" % nextPosition)
        return HttpResponse(t.render(
            guide=guide,
            program=program,
            nextguide=nextguide))

    def snippet(self, request, id):
        # guide = Guide.objects.get(guide_id=guide_id)
        # calm.models.GuideEmailCampaign.objects.filter(guide__id=g.id).first()
        # obj = self.model.objects.filter(guide__id=guide.id).first()
        obj = self.model.objects.filter(pk=id)
        guide = obj.guide
        program = guide.program
        overrides = yaml.safe_load(obj.data)
        obj.iterablegen_campaign
        return HttpResponse(obj.iterablegen_campaign)

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
