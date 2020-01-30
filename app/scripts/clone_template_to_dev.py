import logging
logger = logging.getLogger(__name__)

import app.settings
import re
import json
from hbemail.utils import bulk_update_catalog, update_catalog_item, iterable

response = iterable("/campaigns", method="get")
data = response.json()
campaigns = data.get('campaigns', [])
sendgrids = [cam for cam in campaigns if "sendgrid" in cam['labels']]

TEMPLATE_IDS = ["1366605", "1366606", "1366607",
"1366614", "1366608", "1366613",
"1366615", "1366616", "1366617",
"1366618", "1366619", "1366623",
"1366624", "1366625",
"1366626", "1366627", "1366628",
"1366629", "1366630", "1366631",
"1366632", "1366633", "1366634",
"1366635", "1366636", "1366638",
"1366639", "1366641", "1366645"]
for i, send in enumerate(sendgrids):
    templateId = send['templateId']
    response = iterable("/templates/email/get", method="get", queryArgs={"templateId":templateId})
    if response.status_code == 200:
        templateData = {}
        templateData = response.json()
        # templateData['clientTemplateId'] = templateData['templateId']
        templateData['clientTemplateId'] = templateData['name']
        del templateData['metadata']
        del templateData['templateId']
        del templateData['messageTypeId']
        del templateData['fromEmail']
        response = iterable('/templates/email/upsert', data=templateData, apiKey=app.settings.ITERABLE_API_KEY_DEV)
        template = response.json()
    # campaignData = {
    #     'name':send['name'],
    #     'templateId':int(TEMPLATE_IDS[i]),
    #     'type':'triggered',
    #     'listIds':[384142]
    # }
    # response = iterable('/campaigns/create', data=campaignData, apiKey=app.settings.ITERABLE_API_KEY_DEV)
    # break

# response = iterable('/email/target', data={"campaignId":975717, "recipientEmail":"calmpromotabtesting@gmail.com"}, apiKey=app.settings.ITERABLE_API_KEY_DEV)
