import yaml
import logging
logger = logging.getLogger(__name__)

from .models import (
    Program,
    Guide,
    GuideEmailCampaign)
from rest_framework import serializers


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'

    def create(self, validated_data):
        p = Program(**validated_data)
        p.save()
        logger.debug("serializer: create program")
        return p

    def update(self, instance, validated_data):
        instance.author = validated_data.get('author', instance.author)
        instance.background_image = validated_data.get('background_image', instance.background_image)
        instance.description = validated_data.get('description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.language = validated_data.get('language', instance.language)
        instance.meditation_type = validated_data.get('meditation_type', instance.meditation_type)
        instance.narrator = validated_data.get('narrator', instance.narrator)
        instance.narrator_image = validated_data.get('narrator_image', instance.narrator_image)
        instance.program_id = validated_data.get('program_id', instance.program_id)
        instance.title = validated_data.get('title', instance.title)
        instance.titled_background_image = validated_data.get('titled_background_image', instance.titled_background_image)
        instance.save()
        logging.info("serializer: update program")
        return instance

class GuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guide
        fields = '__all__'

    def create(self, validated_data):
        g = Guide(**validated_data)
        g.save()
        logger.info("serializer: create guide")
        return g

    def yaml_data(self):
        return yaml.dump_all(self.data)

    def update(self, instance, validated_data):
        instance.duration = validated_data.get('duration', instance.guide_id)
        instance.guide_id = validated_data.get('guide_id', instance.guide_id)
        instance.language = validated_data.get('language', instance.language)
        instance.position = validated_data.get('position', instance.position)
        instance.program = validated_data.get('program', instance.program)
        instance.short_title = validated_data.get('short_title', instance.short_title)
        instance.title = validated_data.get('title', instance.title)
        instance.type = validated_data.get('type', instance.type)
        # instance.data = self.yaml_data()
        instance.save()
        logging.info("serializer: update guide")
        return instance

class GuideEmailCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuideEmailCampaign
        fields = '__all__'
