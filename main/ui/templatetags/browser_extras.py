from django.template.defaultfilters import stringfilter
from django.template.defaulttags import register


@register.filter
@stringfilter
def int_to_string(value):
    return value

@register.filter
def get_value(dictionary, key):
    return dictionary.get(key)
