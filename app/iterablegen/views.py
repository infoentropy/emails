import json

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
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
    renderer_classes = (JSONRenderer, XMLRenderer,)

class SnippetViewSet(viewsets.ModelViewSet):
    queryset = IterableSnippet.objects.all()
    serializer_class = IterableSnippetSerializer


class CampaignSnippetViewSet(viewsets.ModelViewSet):
    queryset = IterableCampaignSnippet.objects.all()
    serializer_class = IterableCampaignSnippetSerializer
