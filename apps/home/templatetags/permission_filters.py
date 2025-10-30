from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Returns the value for a given key in a dictionary."""
    return dictionary.get(key) if dictionary else None