from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Django shablonida lug'atdan qiymat olish imkonini beradi.
    Ishlatilishi: {{ my_dictionary|get_item:my_key }}
    """
    return dictionary.get(key)
