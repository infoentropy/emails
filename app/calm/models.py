from django.db import models
import logging
logger = logging.getLogger(__name__)

from .utils import CalmAPI
CALM_API_CLIENT = CalmAPI()

LANGUAGE = [
('en', 'English')
]

MEDITATION_CHOICES = (
    ('meditation', 'Meditation'),
    ('sleep', 'Sleep'),
    ('sequential', 'Sequential'),
    ('masterclass', 'Masterclass'),
)

class CalmModel(models.Model):
    """
    Sync fetched program.
    """
    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def fetch(self):
        raise Exception("You need to define a fetch() for your class")

    def sync(self, serializer, data=None):
        """
        pull a program from Calm API.
        """
        # use data if provided otherwise fetch from API
        logger.debug("sync!!!")
        updated = serializer(self, data=data or self.fetch())
        if updated.is_valid():
            updated.save()
        else:
            raise Exception('did not save correctly %s', updated.errors)
        return updated


# Program, ripped from API
class Program(CalmModel):
    author = models.CharField(max_length=128, null=True, blank=True)
    background_image = models.CharField(max_length=2048, blank=True, null=True)
    description = models.CharField(max_length=2048, blank=True, null=True)
    image = models.CharField(max_length=2048, blank=True, null=True)
    language = models.CharField(choices=LANGUAGE, max_length=16, blank=True, null=True, default='en')
    meditation_type = models.CharField(choices=MEDITATION_CHOICES, blank=True, null=True, max_length=256)
    narrator = models.CharField(max_length=256, blank=True, null=True)
    narrator_image = models.CharField(max_length=2048, blank=True, null=True)
    program_id = models.CharField(max_length=64)
    title = models.CharField(max_length=2048, blank=True, null=True)
    titled_background_image = models.CharField(max_length=2048, blank=True, null=True)

    """
    need to map the CALM id into a field otherwise collision with Django ID
    """
    @staticmethod
    def translate_api_for_serializer(id, data):
        data['program_id'] = data['id']
        data['id'] = id
        return data

    """
    Fetch program from API
    """
    def fetch(self):
        data = CALM_API_CLIENT.get('/programs/%s' % self.program_id)
        return Program.translate_api_for_serializer(self.id, data)

# Guide, ripped from API
class Guide(CalmModel):
    duration = models.FloatField(blank=True, null=True)
    guide_id = models.CharField(max_length=64)
    language = models.CharField(choices=LANGUAGE, max_length=16, blank=True, null=True, default='en')
    position = models.PositiveSmallIntegerField(default=0)
    program = models.ForeignKey('Program', blank=True, null=True, on_delete=models.CASCADE)
    short_title = models.CharField(max_length=256)
    title = models.CharField(max_length=256)
    type = models.CharField(default="audio", max_length=32)

    def __str__(self):
        return "%s: %s (%s)" % (self.program.title, self.title, self.position)

    """
    need to map the CALM id into a field otherwise collision with Django ID
    """
    @staticmethod
    def translate_api_for_serializer(id, data):
        data['guide_id'] = data['id']
        data['id'] = id
        return data

    @property
    def deeplink(self):
        return "https://www.calm.com/player/%s" % self.guide_id

    @property
    def parent_title(self):
        return self.program.title

    def fetch(self):
        data = CALM_API_CLIENT.get('/programs/guides/%s' % self.guide_id)
        for g in data['guides']:
            if g['id'] == self.guide_id:
                return Guide.translate_api_for_serializer(self.id, data)
        return None

class GuideEmailCampaign(models.Model):
    FORMAT_CHOICES = (
        ('htmlmixed', 'html'),
        ('javascript', 'js'),
        ('markdown', 'markdown'),
    )

    guide = models.ForeignKey('Guide', on_delete=models.CASCADE)
    format = models.CharField(default='markdown', max_length=32, choices=FORMAT_CHOICES, blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    test = models.TextField(blank=True, null=True)


    @property
    def render(self):
        pass
