from django import template
import yaml
register = template.Library()

@register.inclusion_tag('snippet.html')
def render_content_snippet(content, *args, **kwargs):
    data = yaml.safe_load(content.data) or {}
    markup = content.snippet.markup
    return {"data":content.data}
    # return {"data":data}

@register.inclusion_tag('campaign.html')
def render_campaign(campaign):
    return {'campaign':campaign}
