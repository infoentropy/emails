import csv, re
from hbemail.utils import iterable
from jinja2 import (
BaseLoader,
Environment,
FunctionLoader,
Template,
select_autoescape,
)
csvfile = open('./scripts/year_in_review_emails-2019_personalized_stats-eec44cfae2d0-2019-12-13-18-16-01.csv', 'r')
reader = csv.DictReader(csvfile)

LAYOUT_TEMPLATE = """
{{#assign "styles"}}
<style type="text/css">
h1,div,p { Margin:0; padding:0; }
h1 { font-weight:400; }
.copy { font-size:18px;Margin:15px 0;color:#6D7278 }
.section { color:#ffffff; font-family: 'Avenir Next', 'Avenir', 'Helvetica', sans-serif; Margin:5px auto 15px auto; max-width:500px;}
.yir { padding:30px 32px 10px 32px; }
.section h1.title { font-size:30px; }
.section1 { background-color:#60B4E7;}
.section2 { background-color:#619FE5;}
.section3 { background-color:#628BE4;}
.section4 { background-color:#6376E2;}
.section5 { background-color:#6461E0;}

.metric { Margin-bottom:60px; }

.metric.minimargin { Margin-bottom:5px; }
.metric.nomargin { Margin-bottom:0px; }

.metric .title { text-transform:uppercase; font-size:12px; letter-spacing:1px; Margin-bottom:10px;}
.metric .value { font-size:26px; line-height:30px;}
.calendar.metric .title { width:46px; Margin-bottom:0;}
.calendar.metric .value { font-size:12px;line-height:12px; }
.bigimage.metric td.image { width:90px;}
.metric a { text-decoration:none; color:#ffffff;}
</style>
<style type="text/css">
@media only screen and (min-width:500px) {
}
</style>
{{/assign}}
{{{ snippet "wrapper - open promocard" button_color="calm-blue blue green" promocard=styles }}}

{{#assign "image"}}https://d15k2d11r6t6rl.cloudfront.net/public/users/Integrators/669d5713-9b6a-46bb-bd7e-c542cff6dd6a/b215951a136f423a9cbb19359fcccb0a/year%20in%20review/2019_Header_2x.png{{/assign}}
{{#assign "title"}}{{/assign}}
{{#assign "body"}}{{/assign}}
{{#assign "description"}}Your Year of Calm 2019{{/assign}}
{{#assign "link"}}https://www.calm.com{{/assign}}
{{#assign "imagestyle"}}{{/assign}}
{{{ snippet 'component - image with optional text' image=image title=title body=body description=description link=link imagestyle=imagestyle }}}

{{#assign "text"}}
<div style="max-width:380px;Margin:40px auto;">
{{#if first_name}}<h1 style="color:#333333;Margin:10px 0 0 0;">{{first_name}},</h1>{{/if}}
<h1 style="color:#333333;Margin:10px 0 0 0;">What a year!</h1>
<p style="Margin:35px 0;font-size:18px;color:#6D7278">Through it all, you made time to invite more peace and relaxation into your life.</p>
<p style="Margin:35px 0;font-size:18px;color:#6D7278">Scroll through to reflect on 2019 and inspire new ways to care for your mind in 2020.</p>
</div>
{{/assign}}
{{#assign "body"}}
{{{ snippet "component - basic text" body=text }}}
{{/assign}}
{{{ snippet "wrapper - table center" body=body }}}

{% block content %}{% endblock %}

{{#assign "body"}}
<tr>
<td>
<div class="section">
    <div style="Margin:40px 0 10px 0; color:#000000;text-align:center;">
        <h1 style="line-height:40px;">Together we're making <br /> the world a little calmer</h1>
        <p style="Margin-top:20px;font-size:18px;color:#6D7278">See Calm's 🌎 Year in Review</p>
    </div>
</div>
</td>
</tr>
{{{ snippet "component - button" color="calm-blue" text="Let's Reflect" link="https://www.calm.com/blog" width="220" }}}
{{{ snippet "component - spacer" height=20 }}}
{{/assign}}
{{{ snippet "wrapper - table center" body=body }}}

{{!-- https://calmdotcom.atlassian.net/browse/LIFE-225 --}}
{{#assign "coupon"}}uTESt8tS{{/assign}}
{{#assign "title"}}Invite friends to join you for a Calm 2020{{/assign}}
{{#assign "text"}}
<p class="copy">Share this personalized link to give them our most generous offer of the season.</p>
{{/assign}}
{{#assign "cta"}}Share the Calm{{/assign}}

{% for offer in SPECIAL_OFFERS %}
{{#eq yir2019segment "_{{offer.audience}}_" }}
{{#assign "coupon"}}_{{offer.coupon}}_{{/assign}}
{{#assign "title"}}_{{offer.title}}_{{/assign}}
{{#assign "cta"}}_{{offer.cta}}_{{/assign}}
{{#assign "text"}}
{% for line in offer.text %}
<p class="copy">_{{line}}_</p>
{% endfor %}
{{/assign}}
{{/eq}}
{% endfor %}
{{#assign "coupon_path"}}new-member-offer{{/assign}}
{{#assign "plan"}}yearly{{/assign}}
{{#assign "couponLink"}}https://www.calm.com{{coupon_path}}?plan={{defaultIfEmpty plan "lifetime"}}&coupon={{coupon_code}}&lifetime_coupon={{coupon_code}}&email={{#urlEncode}}{{email}}{{/urlEncode}}{{/assign}}
{{#assign "escapedCouponLink"}}
https://www.calm.com/nodeeplink?redirect_to={{#urlEncode}}{{{couponLink}}}{{/urlEncode}}
{{/assign}}

{{#assign "body"}}
<div class="section" style="Margin:0 10px">
    <table width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="Margin:30px 0 30px 0;">
    <tr>
    <td>
    <div style="max-width:350px;Margin:0 auto;">
    <h1 style="color:#333333;font-size:24px;line-height:32px;">{{{title}}}</h1>
    {{{text}}}
    <div><a href="{{escapedCouponLink}}">{{cta}}</a></div>
    </div>
    </td>
    </tr>
    </table>
</div>
{{/assign}}
<div style="Margin:0 20px">
{{{ snippet "component - gradient border block" body=body }}}
</div>

{{{ snippet "wrapper - close" }}}
"""

INDEX_TEMPLATE = """
{{!-- Generated by Script --}}
{% extends "layout.html" %}
{% block content %}
{% for sesstype, icon in YIR_SESSION_ICONS.items() %}
{{#eq sess_type_most_freq "_{{sesstype}}_"}}{{#assign "sess_type_most_freq_icon"}}_{{icon}}_{{/assign}}{{/eq}}
{{#eq try_this_sess_type "_{{sesstype}}_"}}{{#assign "try_this_sess_type_icon"}}_{{icon}}_{{/assign}}{{/eq}}
{% endfor %}

{% for key, icon in YIR_SLEEP_GENRE_ICONS.items() %}
{{#eq sleep_story_genre_most_freq "_{{key}}_"}}{{#assign "sleep_story_genre_most_freq_icon"}}_{{icon}}_{{/assign}}{{/eq}}{% endfor %}
{% for key, icon in YIR_TIME_ICONS.items() %}
{{#eq time_of_day_most_freq "_{{key}}_"}}{{#assign "time_of_day_most_freq_icon"}}_{{icon}}_{{/assign}}{{/eq}}{% endfor %}

{{#catalog "Localization" "yearinreview" as |translations| }}
{{#assign "user_lang"}}{{defaultIfEmpty active_language "en"}}{{/assign}}
{{#lookup translations user_lang as |text| }}

{% for section in data_layout %}
{{!-- START SECTION ("_{{section.title.default}}_") --}}
{% if section.title.lookup %}
{{#assign "_title"}}{{#lookup _{{section.title.lookup}}_ as |lookuptitle|}}{{lookuptitle}}{{/lookup}}{{/assign}}
{{_title}}
{% else %}
{{#assign "_title"}}{{{ text._{{section.title.keyname}}_ }}}{{/assign}}
{% endif %}
{{#assign "defaultTitle"}}_{{section.title.default}}_{{/assign}}
<div class="section _{{section.css_class}}_" style="max-width:500px;">
    <div class="yir">
        <div style="Margin-bottom:30px">
        <h1 class="title">{{{ defaultIfEmpty _title defaultTitle }}}</h1>
        {%if section.title.subtitle %}
        <div class="subtitle">_{{section.title.subtitle}}_</div>
        {% endif %}
        </div>
        <div class="body">

{% for metric in section.get('data', []) %}
{{!-- _{{ metric.variable }}_ --}}
{{#if _{{metric.variable}}_ }}
{% if metric.title.lookup %}
{{#lookup text _{{ metric.title.lookup }}_ as |_metricTitle|}}
{{#assign "metricTitle"}}{{{ defaultIfEmpty _metricTitle  "_{{metric.title.default}}_" }}}{{/assign}}
{{/lookup}}
{% else %}
{{#lookup text "_{{metric.title.keyname}}_" as |_metricTitle|}}
{{#assign "metricTitle"}}{{{ defaultIfEmpty _metricTitle  "_{{metric.title.default}}_" }}}{{/assign}}
{{/lookup}}
{% endif %}
{% if 'NNN' in metric.title.default %}
{{#assign "metricTitle"}}{{ replace metricTitle "NNN" _{{metric.title.value}}_ }}{{/assign}}
{% endif %}
{% if metric.lookup %}
    {% if metric.lookup == metric.variable %}
        {{#assign "metricValue"}}{{#lookup text _{{metric.variable}}_ as |word| }}{{word}}{{/lookup}}{{/assign}}
    {% else %}
        {{#assign "_metricValue"}}{{text._{{metric.lookup}}_}}{{/assign}}
        {{#assign "metricValue"}}{{ replace _metricValue "NNN" _{{metric.variable}}_ }}{{/assign}}
    {% endif %}
{% else %}
    {{#assign "metricValue"}}{{ _{{ metric.variable }}_ }}{{/assign}}
{% endif %}
{{{ snippet "yir metric" icon=_{{ metric.icon or "''"}}_ icon_shape="_{{metric.icon_shape}}_" metrictitle=metricTitle value=metricValue url=_{{metric.url or '""'}}_ css_class="_{{metric.css_class}}_" }}}
{{else}}
{{{ snippet "yir metric" icon=_{{ metric.icon or "''"}}_ icon_shape="_{{metric.icon_shape}}_" metrictitle="_{{metric.title.default}}_" value="_{{metric.ifEmpty}}_" url=_{{metric.url or '""'}}_ css_class="_{{metric.css_class}}_" }}}
{{/if}}

{% endfor %}

        </div>
    </div>
</div>
{{!-- END SECTION ("_{{section.title.default}}_") --}}
{% endfor %}
{{/lookup}}
{{/catalog}}

{% endblock %}
"""

def load_template(name):
    if name == "layout.html":
        return LAYOUT_TEMPLATE
    if name == "index.html":
        return INDEX_TEMPLATE
    return None

env = Environment(
    variable_start_string="_{{",
    variable_end_string="}}_",
    comment_start_string="_{#",
    comment_end_string="#}_",
    loader=FunctionLoader(load_template))
TEMPLATE_SECTION = env.get_template("index.html")
TEMPLATE_ID = 1308659

SPECIAL_OFFERS = []
# [
#     {
#         "audience":"paidsubs",
#         "title":"Invite friends to join you for a Calm 2020",
#         "text":["Share this personalized link to give them our most generous offer of the season."],
#         "coupon":"uTESt8tS",
#         "cta":"Share"
#     },
#     {
#         "audience":"trial",
#         "title":"{{first_name}}, your gift subscription is nearly done.",
#         "text":"",
#         "coupon":"igGxPddj",
#         "cta":"Redeem"
#     },
#     {
#         "audience":"churnsoon",
#         "title":"{{first_name}}, your subscription is nearly done.",
#         "text":["Renew today for 25% off."],
#         "coupon":"8RbI1SfM",
#         "cta":"Redeem"
#     },
#     {
#         "audience":"churned",
#         "title":"{{first_name}}, we’d love to have you back for a 2020 of Calm.",
#         "text":["Renew today for 25% off."],
#         "coupon":"8RbI1SfM",
#         "cta":"Redeem"
#     }
# ]

IMAGE_FOLDER = "https://d15k2d11r6t6rl.cloudfront.net/public/users/Integrators/669d5713-9b6a-46bb-bd7e-c542cff6dd6a/b215951a136f423a9cbb19359fcccb0a/section%20icons/"
YIR_IMAGE_FOLDER = "https://d15k2d11r6t6rl.cloudfront.net/public/users/Integrators/669d5713-9b6a-46bb-bd7e-c542cff6dd6a/b215951a136f423a9cbb19359fcccb0a/year%20in%20review/"
YIR_SESSION_ICONS = {
    "body":YIR_IMAGE_FOLDER + "calm-body.png",
    "breathe":YIR_IMAGE_FOLDER + "breathe.png",
    "":YIR_IMAGE_FOLDER + "Sleep_1x.png",
    "masterclass":YIR_IMAGE_FOLDER + "Masterclasses_1x.png",
    "meditation":YIR_IMAGE_FOLDER + "Meditate_1x.png",
    "music":YIR_IMAGE_FOLDER + "Music_1x.png",
    "sleep_story":YIR_IMAGE_FOLDER + "Sleep_1x.png",
}

YIR_TIME_ICONS = {
    "morning":YIR_IMAGE_FOLDER + "Clock_1x.png",
    "afternoon":YIR_IMAGE_FOLDER + "Clock_1x.png",
    "evening":YIR_IMAGE_FOLDER + "Clock_1x.png",
    "middle_night":YIR_IMAGE_FOLDER + "Clock_1x.png",
    "":YIR_IMAGE_FOLDER  + "Clock_1x.png"
}

YIR_SLEEP_GENRE_ICONS = {
    "Fiction":YIR_IMAGE_FOLDER + "fiction.png",
    "Nonfiction":YIR_IMAGE_FOLDER + "nonfiction.png",
    "Nature":YIR_IMAGE_FOLDER + "nature.png",
    "Naps":YIR_IMAGE_FOLDER + "naps.png",
}

BOOL_VARS = {
    'had_one_plus_sessions',
    'had_one_plus_sleep_stories',
    'had_one_plus_music_minutes',
    'is_german'
}

INT_VARS = {
    'n_sess_type_most_freq',
    'music_minutes',
    'n_sleep_story_genre_most_freq',
    'n_sess_most_freq_sleep_story_narrator',
    'n_sess_most_freq_sleep_story_title',
}

year_in_review_sections = [
    {
        "title": {
            "default":"{{#if first_name}}{{first_name}}'s{{else}}Your{{/if}} Year of Calm",
            "keyname": "sectiontitle_yearofcalm",
        },
        "css_class":"section1",
        "style": {
            "bg_color":"#000000",
            "bg_image":"",
            "color":"#ffffff",
        },
        "data":[
            {
                "title":{
                    "default":"Your Calm Go-To",
                    "keyname":"metricMostFreq",
                    "value":"sess_type_most_freq",
                },
                "variable":"sess_type_most_freq",
                "lookup":"sess_type_most_freq",
                "icon": "\"%s%s\"" % (YIR_IMAGE_FOLDER, "Heart_1x.png"),
                "icon_shape":"square",
                "ifEmpty":"--"
            },
            {
                "title":{
                    "default":"Your Sessions",
                    "keyname":"sess_type_most_freq",
                    "value":"sess_type_most_freq",
                    "lookup":"sess_type_most_freq",
                },
                "variable":"n_sess_type_most_freq",
                "icon":"sess_type_most_freq_icon",
                "icon_shape":"circle",
                "lookup":'numtimes',
                "ifEmpty":"0"
            },
            ]
    },
    {
        "title": {
            "default":"{{#if first_name}}{{first_name}}'s{{else}}Your{{/if}} Calm Time",
            "keyname": "sectiontitle_calmtime",
        },
        "css_class":"section2",
        "icon":"square",
        "style": {
            "bg_color":"#666666",
            "bg_image":"",
            "color":"#ffffff",
        },
        "data":[
            {
                "title":{
                    "default":"Most Mindful Time of the Day",
                    "keyname":"metricMostCommonTime",
                    "value":"time_of_day_most_freq"
                },
                "variable":"time_of_day_most_freq",
                "lookup":"time_of_day_most_freq",
                "icon": "time_of_day_most_freq_icon",
                "icon_shape":"square",
                "ifEmpty":"afternoon",
            },
            {
                "title":{
                    "default":"Most Common Day you Chose Calm",
                    "keyname":"metricMostCommonDay",
                    "value":"day_of_week_most_freq"
                },
                "variable":"day_of_week_most_freq",
                "icon": "\"%s%s\"" % (YIR_IMAGE_FOLDER, "Calendar_1x.png"),
                "icon_shape":"square",
                "css_class":"minimargin",
                "ifEmpty":"wednesday",
            },
            {
                "title":{
                    "default":"SUN",
                    "keyname":"sunday",
                    "value":""
                },
                "variable":"viz_n_day_of_week_sun",
                "icon": "",
                "css_class": "calendar nomargin",
                "ifEmpty":"",
            },
            {
                "title":{
                    "default":"MON",
                    "keyname":"monday",
                    "value":""
                },
                "variable":"viz_n_day_of_week_mon",
                "icon": "",
                "css_class": "calendar nomargin",
                "ifEmpty":"",
            },
            {
                "title":{
                    "default":"TUE",
                    "keyname":"tuesday",
                    "value":""
                },
                "variable":"viz_n_day_of_week_tue",
                "icon": "",
                "css_class": "calendar nomargin",
                "ifEmpty":"",
            },
            {
                "title":{
                    "default":"WED",
                    "keyname":"wednesday",
                    "value":""
                },
                "variable":"viz_n_day_of_week_wed",
                "icon": "",
                "css_class": "calendar nomargin",
                "ifEmpty":"",
            },
            {
                "title":{
                    "default":"THU",
                    "keyname":"thursday",
                    "value":""
                },
                "variable":"viz_n_day_of_week_thu",
                "icon": "",
                "css_class": "calendar nomargin",
                "ifEmpty":"",
            },
            {
                "title":{
                    "default":"FRI",
                    "keyname":"friday",
                    "value":""
                },
                "variable":"viz_n_day_of_week_fri",
                "icon": "",
                "css_class": "calendar nomargin",
                "ifEmpty":"",
            },
            {
                "title":{
                    "default":"Sat",
                    "keyname":"saturday",
                    "value":""
                },
                "variable":"viz_n_day_of_week_sat",
                "icon": "",
                "css_class": "calendar",
                "ifEmpty":"",
            },
            ]
    },
    {
        "title": {
            "default":"{{#if first_name}}{{first_name}}'s{{else}}Your{{/if}} Bedtime with Calm",
            "keyname": "sectiontitle_bedtime",
        },
        "css_class":"section3",
        "style": {
            "bg_color":"#999999",
            "bg_image":"",
            "color":"#ffffff",
        },
        "data":[
            {
                "title":{
                    "default":"Favorite Sleep Story",
                    "keyname":"metricFavSleep",
                    "value":"n_sess_most_freq_sleep_story_title"
                },
                "variable":"most_freq_sleep_story_title",
                "icon":"most_freq_sleep_story_icon_url",
                "icon_shape":"rounded",
                "url":"most_freq_sleep_story_program_url",
                "css_class": "bigimage minimargin",
                "ifEmpty":"--",
            },
            {
                "title":{
                    "default":"Which took you to dreamland",
                    "keyname":"metricFavSleepCount",
                    "value":"n_sess_most_freq_sleep_story_title"
                },
                "variable":"n_sess_most_freq_sleep_story_title",
                "icon":"",
                "icon_shape":"",
                "css_class": "bigimage",
                "lookup": 'numtimes',
                "ifEmpty":"0",
            },
            {
                "title":{
                    "default":"Favorite Sleep Story Narrator",
                    "keyname":"metricFavNarrator",
                    "variable":"sleep_story_genre_most_freq"
                },
                "variable":"most_freq_sleep_story_narrator",
                "icon":"narrator_headshot_url",
                "icon_shape":"circle",
                "url":"narrator_url",
                "css_class": "bigimage minimargin",
                "ifEmpty":"--",
            },
            {
                "title":{
                    "default":"Who lulled you to sleep",
                    "keyname":"metricFavNarratorCount",
                    "value":"n_sess_most_freq_sleep_story_narrator"
                },
                "variable":"n_sess_most_freq_sleep_story_narrator",
                "icon":"",
                "icon_shape":"circle",
                "css_class": "bigimage",
                "lookup": 'numtimes',
                "ifEmpty":"0",
            },
            {
                "title":{
                    "default":"Favorite Sleep Story Genre",
                    "keyname":"metricFavSleepGenre",
                    "value":"sleep_story_genre_most_freq"
                },
                "variable":"sleep_story_genre_most_freq",
                "icon":"sleep_story_genre_most_freq_icon",
                "icon_shape":"circle",
                "css_class": "bigimage minimargin",
                "ifEmpty":"--",
            },
            {
                "title":{
                    "default":"You Listened",
                    "keyname":"metricFavSleepGenreCount",
                    "value":"try_this_sess_type"
                },
                "variable":"n_sleep_story_genre_most_freq",
                "icon": "",
                "icon_shape":"circle",
                "css_class": "bigimage",
                "lookup": 'numtimes',
                "ifEmpty":"0",
            },
            ]
    },
    {
        "title": {
            "default":"Yours to Discover",
            "keyname": "sectiontitle_discover",
            "subtitle":"We like your style. Here are a few recommendations we think you’ll like.",
        },
        "css_class":"section4",
        "style": {
            "bg_color":"#aaaaaa",
            "bg_image":"",
            "color":"#ffffff",
        },
        "data":[
            {
                "title":{
                    "default":"NNN",
                    "keyname":"metricTrySession",
                    "value":"try_this_sess_type"
                },
                "variable":"try_this_sess_type_guide_title",
                "icon":"try_this_sess_type_icon",
                "icon_shape":"circle",
                "url":"try_this_sess_type_program_url",
                "css_class": "bigimage",
                "ifEmpty":"Meditation",
            },
            {
                "title":{
                    "default":"NNN",
                    "keyname":"metricTrySleep",
                    "value":"try_this_sleep_story_genre"
                },
                "variable":"try_this_sleep_story_genre_guide_title",
                "icon":"try_this_sleep_story_genre_icon_url",
                "icon_shape":"circle",
                "url":"try_this_sleep_story_genre_program_url",
                "css_class": "bigimage",
                "ifEmpty":"Afternoon Nap",
            },
            ]
    },
]



# return a Templated string suitable for stuffing user's data
TEMPLATE_SKELETON = TEMPLATE_SECTION.render(
    data_layout = year_in_review_sections,
    YIR_SESSION_ICONS=YIR_SESSION_ICONS,
    YIR_SLEEP_GENRE_ICONS=YIR_SLEEP_GENRE_ICONS,
    YIR_TIME_ICONS=YIR_TIME_ICONS,
    SPECIAL_OFFERS=SPECIAL_OFFERS,
    )
htmlfile = open('./scripts/sample.html', 'w')
htmlfile.write(TEMPLATE_SKELETON)
htmlfile.close()

TEMPLATE_ID = 1308659
response = iterable('/templates/email/update', data={"templateId":TEMPLATE_ID, "html":TEMPLATE_SKELETON})
print(response)
