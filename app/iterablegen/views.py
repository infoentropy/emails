import json

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

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


class SnippetViewSet(viewsets.ModelViewSet):
    queryset = IterableSnippet.objects.all()
    serializer_class = IterableSnippetSerializer


class CampaignSnippetViewSet(viewsets.ModelViewSet):
    queryset = IterableCampaignSnippet.objects.all()
    serializer_class = IterableCampaignSnippetSerializer