import logging
logger = logging.getLogger(__name__)

from datetime import datetime

import json
import time

import calm
from hbemail.utils import bulk_update_catalog, update_catalog_item, iterable
from calm.utils import CalmAPI
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

class CalmProgram(object):
    def __init__(self, **kwargs):
        self.author = kwargs.get('author','')
        self.backgroundImage = kwargs.get('background_image','')
        self.description = kwargs.get('description','')
        self.image = kwargs.get('image','')
        self.freeness = kwargs.get('freeness', '')
        self.key = kwargs.get('id','')
        self.language = kwargs.get('language','')
        self.meditationType = kwargs.get('meditation_type','')
        self.narrator = kwargs.get('narrator','')
        self.narratorImage = kwargs.get('narrator_image','')
        self.programId = kwargs.get('id','')
        self.title = kwargs.get('title','')
        self.titledBackgroundImage = kwargs.get('titled_background_image','')
        self.cCreatedAt = kwargs.get('created_at', '')
        self.cUpdatedAt = kwargs.get('updated_at', '')

        self.featured = kwargs.get('featured', False)
        self.free = kwargs.get('free', False)
        self.isNew = kwargs.get('is_new', False)
        self.isComingSoon = kwargs.get('is_coming_soon', False)
        self.position = kwargs.get('position', 0)
        self.published = kwargs.get('published', False)

class CalmProgramCatalogSerializer(serializers.Serializer):
    class Meta:
        fields = '__all__'

    author = serializers.CharField(max_length=128)
    backgroundImage = serializers.CharField(max_length=2048, required=False)
    description = serializers.CharField(max_length=2048)
    image = serializers.CharField(max_length=2048)
    freeness = serializers.CharField(max_length=32)
    key = serializers.CharField(max_length=64)
    language = serializers.CharField(max_length=16, default='en')
    meditationType = serializers.CharField(max_length=256)
    narrator = serializers.CharField(max_length=256)
    narratorImage = serializers.CharField(max_length=2048, required=False)
    programId = serializers.CharField(max_length=64)
    title = serializers.CharField(max_length=2048)
    titledBackgroundImage = serializers.CharField(max_length=2048, required=False)
    cCreatedAt = serializers.DateField()
    cUpdatedAt = serializers.DateField()

    featured = serializers.BooleanField(required=False)
    free = serializers.BooleanField(required=False)
    isNew = serializers.BooleanField(required=False)
    isComingSoon = serializers.BooleanField(required=False)
    position = serializers.IntegerField()
    published = serializers.BooleanField(required=False)


CALM_API_CLIENT = CalmAPI()
data = CALM_API_CLIENT.get('/programs')
documents = {}

for p in data.get('programs', []):
    g = p['guides']
    del p['guides']
    key = p['id'].replace("_", "UU").replace("-", "DD")
    p['program_id'] = p['id']
    created_at = datetime.strptime(p['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
    updated_at = datetime.strptime(p['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
    p['created_at'] = datetime.strftime(created_at, '%Y-%m-%d') # %H:%M:%S -0:00
    p['updated_at'] = datetime.strftime(updated_at, '%Y-%m-%d')
    prog = CalmProgram(**p)
    ser = CalmProgramCatalogSerializer(prog)
    documents[key] = ser.data
    if len(documents) >= 1000:
        response = bulk_update_catalog('CalmPrograms', documents)
        print("BULK UPDATE %s" % len(documents), response)
        documents = {}
        timer.sleep(1)

response = bulk_update_catalog('CalmPrograms', documents)
print("BULK UPDATE %s" % len(documents), response)
if response.status_code != 202:
    print(response.content)
documents = {}


def defineFieldMappings():
    mappings = {
        "mappingsUpdates": [
          {
            "fieldName":"author",
            "fieldType":"string",
          },
          {
            "fieldName":"backgroundImage",
            "fieldType":"string",
          },
          {
            "fieldName":"description",
            "fieldType":"string",
          },
          {
            "fieldName":"image",
            "fieldType":"string",
          },
          {
            "fieldName":"freeness",
            "fieldType":"string",
          },
          {
            "fieldName":"key",
            "fieldType":"string",
          },
          {
            "fieldName":"language",
            "fieldType":"string",
          },
          {
            "fieldName":"meditationType",
            "fieldType":"string",
          },
          {
            "fieldName":"narrator",
            "fieldType":"string",
          },
          {
            "fieldName":"narratorImage",
            "fieldType":"string",
          },
          {
            "fieldName":"program_id",
            "fieldType":"string",
          },
          {
            "fieldName":"title",
            "fieldType":"string",
          },
          {
            "fieldName":"titledBackgroundImage",
            "fieldType":"string",
          },
          {
            "fieldName":"cCreatedAt",
            "fieldType":"date",
          },
          {
            "fieldName":"cUpdatedAt",
            "fieldType":"date",
          },
          {
            "fieldName":"featured",
            "fieldType":"boolean",
          },
          {
            "fieldName":"free",
            "fieldType":"boolean",
          },
          {
            "fieldName":"isNew",
            "fieldType":"boolean",
          },
          {
            "fieldName":"isComingSoon",
            "fieldType":"boolean",
          },
          {
            "fieldName":"published",
            "fieldType":"boolean",
          },
          {
            "fieldName":"position",
            "fieldType":"long",
          },
        ]
    }
    response = iterable('/catalogs/{catalogName}/fieldMappings'.format(catalogName='CalmPrograms'),
        data=mappings,
        method='put')
    return response

# defineFieldMappings()
