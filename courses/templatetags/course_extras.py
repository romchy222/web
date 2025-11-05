from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Получение значения из словаря по ключу в шаблоне."""
    if dictionary and hasattr(dictionary, 'get'):
        return dictionary.get(key, False)
    elif dictionary and isinstance(dictionary, dict):
        return dictionary.get(key, False)
    return False