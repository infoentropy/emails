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

def send_to_iterable(templateId, payload):
    ITERABLE_URL = "https://api.iterable.com"
    UPDATE_TEMPLATE_ENDPOINT = "/api/templates/email/update"
    UPDATE_TEMPLATE_PARAMS = {
        "templateId":templateId,
        "html": payload,
    }
    url = ITERABLE_URL + UPDATE_TEMPLATE_ENDPOINT
    response = requests.post(url,
        params={"apiKey":settings.ITERABLE_API_KEY},
        json=UPDATE_TEMPLATE_PARAMS
        )
    return response
