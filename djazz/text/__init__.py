from djazz.text.formatter import Formatter
from djazz.text.processor import Processor

class TemplateFormatter(Formatter):
    
    template_name = None
    
    def format(self, text):
        from django.template import Context, loader
        from djazz.conf import settings as default_settings
        
        c = Context({'text': text})
        tpl = loader.get_template(self.template_name)
        return tpl.render(c)


class DefaultFormatter(TemplateFormatter):
    template_name = 'djazz/formatters/default.html'


class RawFormatter(TemplateFormatter):
    template_name = 'djazz/formatters/raw.html'
