from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def div(value, divisor):
    """
    Divise une valeur par un diviseur.
    Usage: {{ value|div:divisor }}
    """
    try:
        value = Decimal(str(value))
        divisor = Decimal(str(divisor))
        
        if divisor == 0:
            return 0
            
        result = value / divisor
        return result
    except (ValueError, InvalidOperation, TypeError):
        return 0
