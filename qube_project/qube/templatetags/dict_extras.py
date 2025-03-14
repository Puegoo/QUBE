from django import template

register = template.Library()

@register.filter
def dict_key(d, key):
    """Zwraca d.get(key), lub None, jeśli klucza nie ma."""
    if d is None:
        return None
    return d.get(key)
