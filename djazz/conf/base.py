from django.conf import settings as django_settings


class Settings(object):
    def __init__(self, settings = django_settings, defaults = {}):
        
        if not settings:
            settings = django_settings
        
        defaults = defaults.copy()
        current = getattr(settings, 'DJAZZ', {}).copy()
        defaults.update(current)
        settings.DJAZZ = defaults
        
        self.settings = settings
    
    def __getitem__(self, key):
        return self.settings[key]
    
    def __setitem__(self, key, value):
        self.settings[key] = value
    
    def __delitem__(self, key):
        del self.settings[key]
    
    def __iter__(self):
        return self.settings.iterkeys()
    
    def __contains__(self, key):
        return key in self.settings