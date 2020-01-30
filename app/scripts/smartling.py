import logging
logger = logging.getLogger(__name__)

import requests
import app.settings as settings
import yaml
from hbemail.utils import bulk_update_catalog, update_catalog_item, iterable

SMARTLING_URL = "https://api.smartling.com"
AUTH_API = "/auth-api/v2"
FILES_API = "/files-api/v2"
LOCALES_API = "/locales-api/v2"
PROJECTS_API = "/projects-api/v2"
MARKETING_PROJECT_ID = "d584f2fa5"

LOCALES = [
("de-DE", "de"),
("es-MX", "es")
]

token = None
refreshToken = None
response = requests.post( SMARTLING_URL + AUTH_API + "/authenticate", json={"userIdentifier":settings.SMARTLING_USER, "userSecret":settings.SMARTLING_SECRET})
if response.status_code == 200:
    data = response.json().get('response').get('data', {})
    accessToken = data.get('accessToken')
    refreshToken = data.get('refreshToken')

for smartling_locale,iterable_locale in LOCALES:
    response = requests.get( SMARTLING_URL + FILES_API + "/projects/{projectId}/locales/{localeId}/file".format(projectId=MARKETING_PROJECT_ID, localeId=smartling_locale),
        headers={"Authorization": "Bearer %s" % accessToken},
        params={"fileUri":"lifecycle_emails.yaml", "retrievalType":"published", "includeOriginalStrings":False})
    locale_file = yaml.safe_load(response.text)
    # for keyname, keystrings in locale_file.items():
    #     stringdata = {}
    #     stringdata[keyname] = {}
    #     stringdata[keyname][iterable_locale] = keystrings
    #     # send to Iterable catalog
    #     response = bulk_update_catalog('SmartlingExample', stringdata)
