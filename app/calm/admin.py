import json
import yaml
import logging
logger = logging.getLogger(__name__)

from jinja2 import Template

from django.contrib import (admin,messages)
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
    readonly_fields = ['link', 'position', 'guide_id', 'language', ]
    fields = ['link', 'guide_id', 'position', 'language',]

    def link(self, obj):
        return format_html('<a href="{}">{}</a>', reverse('admin:calm_guide_change', args=(obj.id,)), obj.short_title)
    link.allow_tags = True


class GuideEmailCampaignInlineAdmin(admin.StackedInline):
    model = GuideEmailCampaign
    extra = 1

class ProgramAdmin(admin.ModelAdmin):
    model = Program
    inlines = [GuideInlineAdmin]
    readonly_fields = ['import_program_link', 'author', 'description', 'language', 'meditation_type', 'narrator', 'title']
    fields = ['program_id', 'title',
        'background_image', 'image',
        'narrator_image', 'titled_background_image',
        'language', 'description',
        'meditation_type', 'import_program_link']

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('<int:id>/import',
            self.admin_site.admin_view(self.import_program_view),
            name='admin_import'),
        ]
        return my_urls + urls

    def import_program_link(self, obj):
        if obj and obj.id:
            # url = reverse('admin_import', args=(obj.id, ))
            return format_html('<a href="{}">Import</a>', '../import')
        else:
            return "Save first"
    import_program_link.allow_tags = True

    def import_program_view(self, request, id):
        context = dict(self.admin_site.each_context(request))
        program = self.model.objects.get(pk=id)
        data = program.fetch()
        updated = program.sync(ProgramSerializer, data=data)

        # check and update child guides.
        update_count = 0
        if updated.is_valid():
            for g in data['guides']:
                guide_data = Guide.translate_api_for_serializer(None, g)
                try:
                    guide = Guide.objects.get(guide_id=g['guide_id'])
                    guide.sync(GuideSerializer, data=guide_data)
                    update_count += 1
                except:
                    del g['id']
                    g['program'] = id
                    guide = GuideSerializer(data=guide_data)
                    if guide.is_valid():
                        g = guide.save()
                        logger.debug("saved guide", g)
                    else:
                        raise
        # return HttpResponse(updated.errors or updated)
        messages.add_message(request, messages.INFO, "Updated %s guides" % update_count)
        return HttpResponseRedirect(reverse('admin:calm_program_change', args=(id, )))


class GuideAdmin(admin.ModelAdmin):
    model = Guide
    search_fields = ['title', 'guide_id', 'program__title']
    ordering = ('program__title', 'position', 'title' , )
    list_display = ['program_title', 'position', 'title', 'meditation_type', 'a_deeplink']
    fields = ['title', 'program', 'guide_id', 'a_deeplink', 'position', 'yaml_data', 'data', ]
    readonly_fields = ['title', 'a_deeplink', 'guide_id', 'yaml_data', 'program', 'position', 'import_guide_link']
    inlines = []

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('<int:id>/import',
            self.admin_site.admin_view(self.import_guide_view),
            name='admin_import_guide'),
        ]
        return my_urls + urls

    def import_guide_view(self, request, id):
        context = dict(self.admin_site.each_context(request))
        program = self.model.objects.get(pk=id)
        data = program.fetch()
        updated = program.sync(ProgramSerializer, data=data)

        # check and update child guides.
        update_count = 0
        if updated.is_valid():
            for g in data['guides']:
                guide_data = Guide.translate_api_for_serializer(None, g)
                try:
                    guide = Guide.objects.get(guide_id=g['guide_id'])
                    guide.sync(GuideSerializer, data=guide_data)
                    update_count += 1
                except:
                    del g['id']
                    g['program'] = id
                    guide = GuideSerializer(data=guide_data)
                    if guide.is_valid():
                        g = guide.save()
                        logger.debug("saved guide", g)
                    else:
                        raise
        # return HttpResponse(updated.errors or updated)
        messages.add_message(request, messages.INFO, "Updated %s guides" % update_count)
        return HttpResponseRedirect(reverse('admin:calm_guide_change', args=(id, )))

    def import_guide_link(self, obj):
        if obj and obj.id:
            return format_html('<a href="{}">Import</a>', '../import')
        else:
            return "Save first"
    import_guide_link.allow_tags = True

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = GuideForm
        return super().get_form(request, obj, **kwargs)

    def program_title(self, obj):
        return format_html('<a href="{}">{}</a>', reverse('admin:calm_program_change', args=(obj.program.id,)), obj.program.title)
    program_title.allow_tags = True
    program_title.short_description = "Program"

    def meditation_type(self, obj):
        return obj.program.meditation_type

    def program_id(self, obj):
        return format_html('<a target="api" href="https://api.app.aws-prod.useast1.calm.com/programs/{}">{}</a>', obj.program.program_id, obj.program.program_id)
    program_id.allow_tags = True
    program_id.short_description = "API Link"

    def a_deeplink(self, obj):
        return format_html('<a href="{}">{}</a>', obj.deeplink, obj.deeplink)
    a_deeplink.allow_tags = True
    a_deeplink.short_description = "Player Link"

    def yaml_data(self, obj):
        from .serializers import (GuideSerializer)
        g = dict(GuideSerializer(obj).data)
        g['link'] = obj.deeplink
        g['content_type'] = obj.program.meditation_type
        g['description'] = obj.program.description
        g['image'] = obj.program.titled_background_image
        g['bg_image'] = obj.program.background_image
        for k in ['id', 'duration', 'data', 'guide_id', 'language', 'position', 'program', 'short_title', 'type']:
            g.pop(k)
        return format_html('<pre style="background-color:#efefef;">{}</pre>', yaml.dump(g))
    yaml_data.allow_tags = True
    yaml_data.short_description = "Common YAML"


class GuideEmailCampaignAdmin(admin.ModelAdmin):
    model = GuideEmailCampaign
    ordering = ('guide__program__title', 'guide__position', 'guide__title' , )
    # list_display = ['guide__program_title', 'guide__position', 'guide__title', ]
    readonly_fields = ['mylink', ]
    extra = 0

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

    def mylink(self, obj):
        return 'foo'
        if obj and obj.id:
            return format_html('<a href="{}" target="render">Show snippets</a>',
                        reverse('email-render', args=[obj.id]))
        else:
            return "Save first"
    mylink.allow_tags = True


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
            if overrides:
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
