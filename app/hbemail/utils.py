import logging
logger = logging.getLogger(__name__)

import requests

from app import settings
from app.widgets import MjmlExtension
from jinja2 import (
BaseLoader,
Environment,
FunctionLoader,
Template as Jinja,
select_autoescape,
)
UPDATE_TEMPLATE_ENDPOINT = "/templates/email/update"

def iterable(path, data=None, **kwargs):
    ITERABLE_URL = "https://api.iterable.com/api"
    url = ITERABLE_URL + path
    http_method = requests.post

    if kwargs.get('method', '') == 'patch':
        http_method = requests.patch
    elif kwargs.get('method', '') == 'put':
        http_method = requests.put

    print(url, http_method)
    response = http_method(url,
        params={"apiKey":settings.ITERABLE_API_KEY},
        json=data
        )
    return response


def send_to_iterable(**kwargs):
    """
    Update a HTML template
    """
    UPDATE_TEMPLATE_PARAMS = {
        "templateId":kwargs.get('templateId',''),
        "html": kwargs.get('html',''),
        "preheaderText": kwargs.get('preheaderText',''),
        "subject": kwargs.get('subject',''),
    }
    logger.debug(UPDATE_TEMPLATE_PARAMS)
    response = iterable(UPDATE_TEMPLATE_ENDPOINT, data=UPDATE_TEMPLATE_PARAMS)
    return response

def update_catalog_item(catalog, itemId, data, **kwargs):
    data = {
        "value":data
    }
    return iterable('/catalogs/%s/items/%s' % (catalog, itemId), data=data, method='put')


def bulk_update_catalog(catalog, documents, **kwargs):
    data = {
        "documents":documents
    }
    return iterable('/catalogs/%s/items' % catalog, data=data, method='post')
