import json

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
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

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = IterableCampaign.objects.all()
    serializer_class = IterableCampaignSerializer
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

class SnippetViewSet(viewsets.ModelViewSet):
    queryset = IterableSnippet.objects.all()
    serializer_class = IterableSnippetSerializer


class CampaignSnippetViewSet(viewsets.ModelViewSet):
    queryset = IterableCampaignSnippet.objects.all()
    serializer_class = IterableCampaignSnippetSerializer
