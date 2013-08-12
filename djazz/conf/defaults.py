from djazz.conf.base import Settings

default_settings = {
    'FORMATTERS': {
        'default': 'djazz/posts/formatters/default.html',
        'raw': 'djazz/posts/formatters/raw.html'
    }
}



settings = Settings(defaults=default_settings)
