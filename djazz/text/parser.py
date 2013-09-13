from django.utils.html_parser import HTMLParser


class FilteredHTMLParser(HTMLParser):
    
    def __init__(self, *args, **kwargs):
        self.allowed_tags = []
        self.filtered_text = None
        HTMLParser.__init__(self, *args, **kwargs)
    
    def allow_tag(self, tag):
        if not tag in self.allowed_tags:
            self.allowed_tags.append(tag)
    
    def allow_tags(self, tags):
        for tag in tags:
            self.allow_tag(tag)
    
    def deny_tag(self, tag):
        if tag in self.allowed_tags:
            self.allowed_tags.pop(self.allowed_tags.index(tag))
    
    def deny_tags(self, tags):
        for tag in tags:
            self.deny_tag(tag)
    
    def feed(self, data):
        self.istart = 0
        self.istop = 0
        self.filtered_text = ''
        self.raw_text = data
        
        retval = HTMLParser.feed(self, data)
        self.filtered_text += self.raw_text[self.istop:]
        
        return retval
    
    def parse_starttag(self, i):
        self.istart = i
        self.istop = HTMLParser.parse_starttag(self, i)
        return self.istop
    
    def parse_endtag(self, i):
        self.istart = i
        self.istop = HTMLParser.parse_endtag(self, i)
        return self.istop
    
    
    def handle_starttag(self, tag, attrs):
        self.filter(tag, self.get_starttag_text())
    
    def handle_endtag(self, tag):
        self.filter(tag, '</%s>' % tag)
    
    def handle_startendtag(self, tag, attrs):
        self.filter(tag, self.get_starttag_text())

    def filter(self, tag, tag_content):
        current = self.istart
        last = self.istop
        
        self.filtered_text += self.raw_text[last:current]
        
        if not tag in self.allowed_tags:
            tag_content = '&lt;' + tag_content[1:-1] + '&gt;'
        
        self.filtered_text += tag_content
        self.lastpos = current
