# Create a new file: templatetags/dict_extras.py
# Make sure to create an __init__.py file in the templatetags directory

from django import template

register = template.Library()

@register.filter
def key(d, key_name):
    """
    Custom filter to access dictionary values by key in Django templates
    Usage: {{ dict|key:key_name }}
    """
    try:
        return d[key_name]
    except (KeyError, TypeError):
        return None
    

def lookup(dictionary, key):
    """Template filter to look up dictionary values by key"""
    if dictionary and key:
        return dictionary.get(key)
    return None