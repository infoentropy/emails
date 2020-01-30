import logging
logger = logging.getLogger(__name__)

import re
import json
from hbemail.utils import bulk_update_catalog, update_catalog_item, iterable
from calm.utils import CalmAPI

RE_NEW_EMAIL = re.compile(r'Email (\d)+:')
RE_SUBJECT = re.compile(r'Subject:[\n\s]?(.*)')
RE_QUOTE = re.compile(r'Quote:[\n\s]?(.*)')
RE_COPY = re.compile(r'Copy:')
RE_NEXT = re.compile(r'Next:')
RE_CTA = re.compile(r'CTA[Ss:]?')
command_start = False


emails = {}
email = None
parsing = None
prev_line_parse = None
data = []
email = {}

PROGRAM_ID = 'mVcvqWcR8C'

CALM_API_CLIENT = CalmAPI()
guidedata = CALM_API_CLIENT.get('/programs/%s' % PROGRAM_ID)

FIELD_DATA_TYPES = {
    "subject":"string",
    "quote":"string",
    "copy":"array",
    "email":"string",
    "cta":"string",
    "programId":"string",
    "guideId":"string",
    "position":"long",
    "nextCopy":"string"
}


with open('./scripts/warren.txt', 'r') as f:
    for i,line in enumerate(f):
        line = line.strip()
        if not line:
            print("\n")
            continue

        if RE_SUBJECT.match(line):
            parsing = 'subject'

        if RE_QUOTE.match(line):
            parsing = 'quote'

        if RE_COPY.match(line):
            parsing = 'copy'

        if RE_NEXT.match(line):
            parsing = 'next'

        if RE_NEW_EMAIL.match(line):
            parsing = 'email'

        if RE_CTA.match(line):
            parsing = 'cta'

        # COMMIT!
        if parsing and prev_line_parse and \
                (prev_line_parse != parsing):
            field_type = FIELD_DATA_TYPES.get(prev_line_parse, None)
            if isinstance(data, list) and field_type == 'string' and len(data):
                data = data[0]
            if field_type == 'array':
                pass
            email[prev_line_parse] = data
            print("commit %s: %s" % (prev_line_parse, data))
            data = []

        # print("parsing %s" % parsing)
        if parsing == 'subject':
            foo = RE_SUBJECT.findall(line)
            if foo:
                subj = foo[0]
            else:
                subj = line
            subj = subj.strip()
            if subj:
                data.append(subj)

        if parsing == 'quote':
            foo = RE_QUOTE.findall(line)
            if foo:
                data.append(foo[0].strip())
            else:
                data.append(line)

        if parsing == 'copy':
            if not RE_COPY.match(line):
                data.append(line)

        if parsing == 'next':
            if not RE_NEXT.match(line):
                data.append(line)

        if parsing == 'cta':
            if not RE_CTA.match(line) and len(data) == 0:
                data.append(line)

        if parsing == 'email':
            print(email)
            print("----NEXT EMAIL----")
            if email:
                position = len(emails)
                g1 = guidedata['guides'][position]
                if position+1 <= len(guidedata['guides']):
                    email['nextGuideId'] = guidedata['guides'][position+1]['id']
                email['position'] = position+1
                email['programId'] = PROGRAM_ID
                email['guideId'] = g1['id']
                g2 = g1['id'].replace('-','DD').replace('_','UU')
                emails[ g2 ] = email
                # emails["%sPOS%s" % (PROGRAM_ID, position) ] =  email
            data = []
            parsing = ''
            email = {}

        prev_line_parse = parsing
#last email
if email:
    position += 1
    g1 = guidedata['guides'][position]
    email['position'] = position+1
    email['programId'] = PROGRAM_ID
    email['guideId'] = g1['id']
    g2 = g1['id'].replace('-','DD').replace('_','UU')
    emails[ g2 ] =  email

print(len(emails))
response = bulk_update_catalog('SequentialWithNext', emails)
