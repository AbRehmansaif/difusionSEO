from django import template
from django.urls import translate_url as django_translate_url

register = template.Library()

@register.filter
def translate_url(path, lang_code):
    """
    Translates the given path to the specified language code.
    Usage in templates:
        {{ request.path|translate_url:'es' }}
    """
    if not path:
        return ''
    return django_translate_url(path, lang_code)
