defaults = {
    'DJAZZ_FORMATTERS': {
        'default': 'djazz/posts/formatters/default.html',
        'raw': 'djazz/posts/formatters/raw.html'
    }
}

def get_default(key, default=None):
    if key in defaults:
        return defaults[key]
    else:
        return default

def get(key, default=None):
    from django.conf import settings
    
    try:
        return getattr(settings, key)
    except AttributeError:
        return get_default(key, default=default)
    

