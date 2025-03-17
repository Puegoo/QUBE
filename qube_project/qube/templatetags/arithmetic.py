from django import template

register = template.Library()

@register.filter
def priority_symbol(value):
    """
    Zamienia 'low', 'medium', 'high' na odpowiednie oznaczenia:
      - low -> "!"
      - medium -> "!!"
      - high -> "!!!"
    """
    mapping = {
        'low': '!',
        'medium': '!!',
        'high': '!!!'
    }
    return mapping.get(value, '?')

@register.filter
def priority_color(value):
    """
    Zwraca kolor CSS zależny od priorytetu:
      - low -> zielony
      - medium -> złoty / żółty
      - high -> czerwony
    """
    mapping = {
        'low': '#3A7D3A',    # zielony
        'medium': '#DAA520', # złoty/żółty
        'high': '#a83232'    # czerwony
    }
    return mapping.get(value, '#666')