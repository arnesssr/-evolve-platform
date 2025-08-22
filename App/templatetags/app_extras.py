from django import template

register = template.Library()

@register.filter(name='lookup')
def lookup(mapping, key):
    """
    Template filter to look up key in a dict-like object or QueryDict.
    Usage: {{ request.GET|lookup:'param' }}
    If mapping is a QueryDict and key endswith _from/_to/_min/_max, you may chain with add in templates,
    but this filter only returns mapping.get(key).
    """
    try:
        if hasattr(mapping, 'get'):
            return mapping.get(key)
        # Fallback for object with attribute access
        return getattr(mapping, key, '')
    except Exception:
        return ''

