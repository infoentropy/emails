import json
import yaml
import logging

logger = logging.getLogger(__name__)

from jinja2 import Template, select_autoescape
from django.utils.html import escape
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action, renderer_classes
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework_xml.parsers import XMLParser
from rest_framework_xml.renderers import XMLRenderer

from .models import (
    IterableCampaignSnippet,
    IterableSnippet,
    IterableCampaign,
)
from .serializers import (
IterableCampaignSnippetSerializer,
IterableSnippetSerializer,
IterableCampaignSerializer,
)

SNIPPET_OUTPUT = "{{{ snippet '%s' %s }}}"
TEMPLATE_BEGIN = '{{{ snippet "wrapper - open" button_color="calm-blue blue green red orange" }}}'
TEMPLATE_END = '{{{ snippet "wrapper - close" }}}'
def center():
    return "\n{{{ snippet 'wrapper - table center' body=output }}}"

def iterable_assign(variable, value):
    return '{{#assign "%s"}}%s{{/assign}}' % (variable, value)

def my_snippet(snippet, args):
    return SNIPPET_OUTPUT % (snippet.name, " ".join(args))

def render_snippet(snippet, guide=None, data=None):
    schema = snippet.schema.strip()
    assign_string = ''
    schema_string = ''
    if schema:
        try:
            schema = yaml.safe_load(schema) or {}
            if data:
                schema.update(data)
            tmpl = Template(json.dumps(schema), autoescape=select_autoescape(['html']))
            rendered = tmpl.render(guide=guide)
            schema = json.loads(rendered)
            schema_string = []
            assign_string = []
            for k,v in schema.items():
                assign_string.append(iterable_assign(k,v))
                schema_string.append('%s=%s' % (k,k))
        except:
            raise
    assigns = "\n".join(assign_string)

    if snippet.needsWrap:
        output = assigns + '\n' + \
            iterable_assign("output", my_snippet(snippet, schema_string) ) + \
            center()
    else:
        output = assigns + '\n' + my_snippet(snippet, schema_string)
    return output + '\n\n'

def render_campaign(campaign):
    output = []
    for s in campaign.iterablecampaignsnippet_set.all():
        data = yaml.safe_load(s.data) or {}
        guide = s.guide
        output.append(render_snippet(s.snippet, guide=guide, data=data))
    return TEMPLATE_BEGIN + "\n".join(output) + TEMPLATE_END

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = IterableCampaign.objects.all()
    serializer_class = IterableCampaignSerializer
    parser_classes = (JSONParser, XMLParser,)
    renderer_classes = (JSONRenderer, XMLRenderer, TemplateHTMLRenderer ,)

    @action(detail=True, methods=['get'])
    def html(self, request, pk=None):
        campaign = self.get_object()
        return Response(
            {'campaign':campaign, "output":render_campaign(campaign)},
            template_name = 'campaign_detail.html')

class SnippetViewSet(viewsets.ModelViewSet):
    queryset = IterableSnippet.objects.all()
    serializer_class = IterableSnippetSerializer
    parser_classes = (JSONParser, XMLParser,)
    renderer_classes = (JSONRenderer, XMLRenderer,  )

class CampaignSnippetViewSet(viewsets.ModelViewSet):
    queryset = IterableCampaignSnippet.objects.all()
    serializer_class = IterableCampaignSnippetSerializer
    parser_classes = (JSONParser, XMLParser,)
    renderer_classes = (JSONRenderer, XMLRenderer,  )
