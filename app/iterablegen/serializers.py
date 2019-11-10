import yaml
import logging
logger = logging.getLogger(__name__)

from rest_framework import serializers
from calm.serializers import (GuideSerializer)

from .models import (
    IterableCampaignSnippet,
    IterableSnippet,
    IterableCampaign,
)

class IterableSnippetSerializer(serializers.ModelSerializer):
    guide = GuideSerializer(read_only=True)
    class Meta:
        model = IterableSnippet
        fields = '__all__'


class IterableCampaignSnippetSerializer(serializers.ModelSerializer):
    campaign = serializers.PrimaryKeyRelatedField(read_only=True)
    snippet = serializers.PrimaryKeyRelatedField(read_only=True)
    guide = serializers.PrimaryKeyRelatedField(read_only=True)
    schema = serializers.SerializerMethodField()

    class Meta:
        model = IterableCampaignSnippet
        fields = '__all__'
        # fields = ['snippet', 'guide', 'data']

    def get_schema(self, instance):
        logging.debug(instance.schema)
        schema = yaml.safe_load(instance.schema) or {}
        return schema

class IterableCampaignSerializer(serializers.ModelSerializer):

    class Meta:
        model = IterableCampaign
        fields = '__all__'
