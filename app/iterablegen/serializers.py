import yaml
import logging
logger = logging.getLogger(__name__)

from rest_framework import serializers

from .models import (
    IterableCampaignSnippet,
    IterableSnippet,
    IterableCampaign,
)

class IterableSnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = IterableSnippet
        fields = ['name', 'needsWrap']


class IterableCampaignSnippetSerializer(serializers.ModelSerializer):
    snippet = IterableSnippetSerializer(read_only=True)
    data = serializers.SerializerMethodField()

    class Meta:
        model = IterableCampaignSnippet
        fields = ['data', 'snippet']

    def get_data(self, instance):
        try:
            logging.debug(instance.snippet.name)
            schema = yaml.safe_load(instance.snippet.schema) or {}
            foo = yaml.safe_load(instance.data) or {}
            schema.update(foo)
            return schema or {}
        except Exception as e:
            raise e

class IterableCampaignSerializer(serializers.ModelSerializer):
    iterablecampaignsnippet_set = serializers.SerializerMethodField()

    class Meta:
        model = IterableCampaign
        # fields = '__all__'
        fields =['url', 'name', 'subject', 'preheaderText', 'iterablecampaignsnippet_set']

    def get_iterablecampaignsnippet_set(self, instance):
        snippets = instance.iterablecampaignsnippet_set.all().order_by('order', 'id')
        return  IterableCampaignSnippetSerializer(snippets, many=True).data
