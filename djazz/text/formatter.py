from djazz.text.processor import Processor

class Formatter(object):
    
    processor = Processor()
    
    def to_html(self, text, silent=True):
        text = self.format(text)
        text = self.processor.process(text, silent=silent)
        return text
    
    def format(self, text):
        m = "Undefined abstract method 'format'"
        raise NotImplementedError(m)
