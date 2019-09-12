import json
import yaml
import logging

logger = logging.getLogger(__name__)

from jinja2 import Template
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.html import escape
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework_xml.parsers import XMLParser
from rest_framework_xml.renderers import XMLRenderer

from iterablegen.serializers import IterableCampaignSerializer

from .models import (
    Program,
    Guide,
    GuideEmailCampaign,
)
from .serializers import (
ProgramSerializer,
GuideSerializer,
GuideEmailCampaignSerializer,
)

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    parser_classes = (JSONParser, XMLParser,)
    renderer_classes = (JSONRenderer, XMLRenderer, TemplateHTMLRenderer, )

    @action(detail=True, methods=['get'])
    def plainrender(self, request, pk=None):
        campaign = self.get_object()
        return Response(
            {'campaign':campaign, "var":"hello world"},
            template_name = 'campaign_detail.html')

    @action(detail=True, methods=['get'])
    def publish(self, request, pk=None):
        campaign = self.get_object()

        # if not settings.ITERABLE_API_KEY:
        #     return Response({"status":"forgot to set iterable api key on environment"})
        return Response({'test':campaign.name})

class GuideViewSet(viewsets.ModelViewSet):
    queryset = Guide.objects.all()
    serializer_class = GuideSerializer


class GuideEmailCampaignViewSet(viewsets.ModelViewSet):
    queryset = GuideEmailCampaign.objects.all()
    serializer_class = GuideEmailCampaignSerializer
    template_name = "guide_email_campaign.html"

    def apply_overrides(self, request):
        obj = self.get_object()
        guide = obj.guide
        program = guide.program
        overrides = yaml.safe_load(obj.data)
        tmp = IterableCampaignSerializer(obj.iterablegen_campaign, context={'request':request})
        usabledata = json.loads(JSONRenderer().render(tmp.data))
        logger.debug(json.dumps(usabledata, indent=2))
        for idx, snippet in enumerate(usabledata['iterablecampaignsnippet_set']):
            orig = snippet['data']
            orig.update(overrides[idx])
            snippet['data'] = orig
            usabledata['iterablecampaignsnippet_set'][idx] = snippet
        nextguide = None
        if program.meditation_type == 'sequential':
            currentPosition = int(guide.position)
            nextPosition = currentPosition+1
            try:
                nextguide = program.guide_set.get(position=nextPosition)
            except:
                logger.info("position %s not here" % nextPosition)
        t = Template(json.dumps(usabledata))
        return json.loads(t.render(guide=guide, program=program, nextguide=nextguide))

    @action(detail=True, methods=['get'])
    def render(self, request, pk=None):
        data = self.apply_overrides(request)

        fudge = []
        fudge.append("""{{{ snippet "wrapper - open" button_color="calm-blue green blue red" }}}""")
        for b in data['iterablecampaignsnippet_set']:
            # set up snippet args
            bdata = b['data']
            body = bdata.get('body')
            description = bdata.get('description')
            if body:
                fudge.append("""{{#assign "body"}}%s{{/assign}}""" % body.strip())
            if description:
                fudge.append("""{{#assign "description"}}%s{{/assign}}""" % description.strip())
            snippety = []
            for key,val in bdata.items():
                if isinstance(val, str):
                    val = val.replace('\n', '')
                if key in ["body", "description"]:
                    snippety.append("%s=%s" % (key, key))
                else:
                    snippety.append("%s=\"%s\"" % (key, val or ''))
            foo = """{{{ snippet "%s" %s }}}""" % (b['snippet']['name'], "\n".join(snippety))
            if b['snippet']['needsWrap']:
                fudge.append("""{{#assign "wrappee"}}%s{{/assign}}""" % foo)
                fudge.append("""{{{ snippet "wrapper - table center" body=wrappee}}}""")
            else:
                fudge.append(foo)
        fudge.append("""{{{ snippet "wrapper - close" }}}""")
        return Response({"text":"\n".join(fudge)})
