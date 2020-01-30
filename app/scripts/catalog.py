import logging
logger = logging.getLogger(__name__)

from datetime import datetime

import json
import time
from app import settings

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

class CalmGuide(object):
    def __init__(self, **kwargs):
        self.key = kwargs.get('id','')
        self.variantId = kwargs.get('variant_id','')
        self.title = kwargs.get('title','')
        self.shortTitle = kwargs.get('short_title','')
        self.narratorId = kwargs.get('narrator_id','')
        self.type = kwargs.get('type', 'audio')
        self.file = kwargs.get('type', 'audio')
        self.cCreatedAt = kwargs.get('created_at', '')
        self.cUpdatedAt = kwargs.get('updated_at', '')
        self.position = kwargs.get('position', 0)
        self.fileSize = kwargs.get('file_size', 0)
        self.duration = kwargs.get('duration', 0)
        self.isFree = kwargs.get('free', False)
        self.isTrailer = kwargs.get('is_trailer', False)

        # parent program updated_at
        self.programId = kwargs.get('program_id', '')
        self.programTitle = kwargs.get('program_title', '')
        self.programMeditationType = kwargs.get('program_meditation_type', '')


class CalmGuideCatalogSerializer(serializers.Serializer):
    class Meta:
        fields = '__all__'

    key = serializers.CharField(max_length=2048)
    variantId = serializers.CharField(max_length=2048)
    title = serializers.CharField(max_length=2048)
    shortTitle = serializers.CharField(max_length=2048)
    narratorId = serializers.CharField(max_length=2048)
    type = serializers.CharField(max_length=2048)
    file = serializers.CharField(max_length=2048)
    cCreatedAt = serializers.DateField()
    cUpdatedAt = serializers.DateField()
    position = serializers.IntegerField(required=False)
    fileSize = serializers.IntegerField(required=False)
    duration = serializers.IntegerField(required=False)
    isFree = serializers.BooleanField(required=False)
    isTrailer = serializers.BooleanField(required=False)

    programId = serializers.CharField(max_length=2048)
    programTitle = serializers.CharField(max_length=2048)
    programMeditationType = serializers.CharField(max_length=2048)

def makeiterablekey(objid):
    # Iterable Catalogs do not allow special characters.
    key = objid.replace("_", "UU").replace("-", "DD")
    return key

def formatTime(timeString):
    # converts API datetime string into Iterable compatible datetime
    tmpTime = datetime.strptime(timeString, '%Y-%m-%dT%H:%M:%S.%fZ')
    return datetime.strftime(tmpTime, '%Y-%m-%d')

def serializeProgram(p):
    p['program_id'] = p['id']
    p['created_at'] = formatTime(p['created_at'])
    p['updated_at'] = formatTime(p['updated_at'])
    prog = CalmProgram(**p)
    ser = CalmProgramCatalogSerializer(prog)
    return ser

def updateGuides(apiKey=None):
    CALM_API_CLIENT = CalmAPI()
    data = CALM_API_CLIENT.get('/programs')
    documents = {}
    for p in data.get('programs', []):
        guides = p['guides']
        for g in guides:
            g['guide_id'] = g['id']
            g['program_id'] = p['id']
            g['program_title'] = p['title']
            g['program_meditation_type'] = p['meditation_type']
            guide = CalmGuide(**g)
            ser = CalmGuideCatalogSerializer(guide)
            documents[makeiterablekey(g['id'])] = ser.data
            if len(documents) >= 1000:
                response = bulk_update_catalog('CalmGuides', documents, apiKey=apiKey)
                print("BULK UPDATE %s %s" % (len(documents), apiKey), response)
                documents = {}

    print("BULK UPDATE %s %s" % (len(documents), apiKey))
    response = bulk_update_catalog('CalmGuides', documents, apiKey=apiKey)
    return response



def updatePrograms(apiKey=None):
    CALM_API_CLIENT = CalmAPI()
    data = CALM_API_CLIENT.get('/programs')
    documents = {}

    for p in data.get('programs', []):
        guides = p['guides']
        programGuides = {}
        del p['guides']
        ser = serializeProgram(p)
        documents[makeiterablekey(p['id'])] = ser.data
        if len(documents) >= 1000:
            response = bulk_update_catalog('CalmPrograms', documents, apiKey=apiKey)
            print("BULK UPDATE %s" % len(documents), response)
            documents = {}
            time.sleep(1)

    response = bulk_update_catalog('CalmPrograms', documents, apiKey=apiKey)
    print("BULK UPDATE %s apiKey=%s" % (len(documents), apiKey), response)
    if response.status_code != 202:
        print(response.content)
    documents = {}
    return response

def defineProgramFieldMappings(apiKey=None):
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
        method='put',
        apiKey=apiKey)
    return response

def defineGuideFieldMappings(apiKey=None):
    mappings = {
        "mappingsUpdates": [
            {
            "fieldName":"key",
            "fieldType":"string",
            },
            {
            "fieldName":"variantId",
            "fieldType":"string",
            },
            {
            "fieldName":"title",
            "fieldType":"string",
            },
            {
            "fieldName":"shortTitle",
            "fieldType":"string",
            },
            {
            "fieldName":"narratorId",
            "fieldType":"string",
            },
            {
            "fieldName":"type",
            "fieldType":"string",
            },
            {
            "fieldName":"file",
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
            "fieldName":"position",
            "fieldType":"long",
            },
            {
            "fieldName":"fileSize",
            "fieldType":"long",
            },
            {
            "fieldName":"duration",
            "fieldType":"long",
            },
            {
            "fieldName":"isFree",
            "fieldType":"boolean",
            },
            {
            "fieldName":"isTrailer",
            "fieldType":"boolean",
            },
            {
            "fieldName":"programId",
            "fieldType":"string",
            },
            {
            "fieldName":"programTitle",
            "fieldType":"string",
            },
            {
            "fieldName":"programMeditationType",
            "fieldType":"string",
            },
        ]
    }
    # response = iterable('/catalogs/{catalogName}'.format(catalogName='CalmGuides'))
    # if response.status_code == 201:
    #     time.sleep(10)
    response = iterable('/catalogs/{catalogName}/fieldMappings'.format(catalogName='CalmGuides'),
        data=mappings,
        method='put',
        apiKey=apiKey)
    return response

# response = defineGuideFieldMappings(apiKey=settings.ITERABLE_API_KEY_DEV)
# response = defineProgramFieldMappings(apiKey=settings.ITERABLE_API_KEY_DEV)
# response = updateGuides(apiKey=settings.ITERABLE_API_KEY_DEV)
response = updatePrograms(apiKey=settings.ITERABLE_API_KEY_DEV)
