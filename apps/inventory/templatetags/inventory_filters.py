from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def number_input(value):
    """
    Formate un nombre pour un input HTML type="number"
    Utilise des points décimaux au lieu de virgules
    """
    if value is None:
        return ''
    
    # Formater avec 2 décimales et remplacer la virgule par un point
    formatted = floatformat(value, 2)
    if formatted:
        return formatted.replace(',', '.')
    return '' 