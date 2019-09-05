import yaml

from rest_framework import serializers

from .models import (
    IterableCampaignSnippet,
    IterableSnippet,
    IterableCampaign,
)

class IterableSnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = IterableSnippet
        fields = ['name']


class IterableCampaignSnippetSerializer(serializers.ModelSerializer):
    snippet = IterableSnippetSerializer(read_only=True)
    data = serializers.SerializerMethodField()

    class Meta:
        model = IterableCampaignSnippet
        fields = ['data', 'snippet']

    def get_data(self, instance):
        try:
            foo = yaml.safe_load(instance.data)
            return foo or {}
        except Exception as e:
            raise e

class IterableCampaignSerializer(serializers.HyperlinkedModelSerializer):
    iterablecampaignsnippet_set = serializers.SerializerMethodField()

    class Meta:
        model = IterableCampaign
        # fields = '__all__'
        fields =['url', 'name', 'subject', 'preheaderText', 'iterablecampaignsnippet_set']

    def get_iterablecampaignsnippet_set(self, instance):
        snippets = instance.iterablecampaignsnippet_set.all().order_by('order', 'id')
        return  IterableCampaignSnippetSerializer(snippets, many=True).data
