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

def send_to_iterable(payload):
    ITERABLE_URL = "https://api.iterable.com"
    UPDATE_TEMPLATE_ENDPOINT = "/api/templates/email/update"
    UPDATE_TEMPLATE_PARAMS = {
        "templateId":1062313,
        # "apiKey":settings.ITERABLE_API_KEY,
        "html": payload,
        "plainText": "hello this is an excellent email.",
    }
    url = ITERABLE_URL + UPDATE_TEMPLATE_ENDPOINT
    response = requests.post(url,
        params={"apiKey":settings.ITERABLE_API_KEY},
        json=UPDATE_TEMPLATE_PARAMS
        )
    return response
