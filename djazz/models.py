from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Config(models.Model):
    section = models.SlugField(blank=True, null=True)
    key = models.SlugField()
    value = models.TextField(null=True, blank=True)
    
    class Meta:
        unique_together = (('section', 'key'))
    
    def __unicode__(self):
        section = self.section or ''
        return section+'.'+self.key


class PostManager(models.Manager):
    POST_TYPE = None
    
    def get_query_set(self):
        q = super(PostManager, self).get_query_set()
        if self.POST_TYPE:
            q = q.filter(type=self.POST_TYPE)
        return q


class Post(models.Model):
    
    class FormatterUnavailable(Exception):
        def __init__(self, fmt):
            m = 'Unavailable formatter %s' % fmt
            super(Post.FormatterUnavailable, self).__init__(m)

    title = models.CharField(max_length=240, null=True, blank=True)
    author = models.ForeignKey(User, related_name="post_author",
                               null=True, blank=True)
    date = models.DateTimeField(blank=True, null=True)
    last_editor = models.ForeignKey(User,null=True, blank=True,
                                    related_name="post_last_editor")
    last_date = models.DateTimeField(blank=True, null=True)
    content = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=25, blank=True, null=True)
    format = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=15, null=True, blank=True)
    
    objects = PostManager()
    
    def __unicode__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.type:
            t = getattr(self.__class__.objects, 'POST_TYPE')
            self.type = t
        super(Post, self).save(*args, **kwargs)
    
    def to_html(self, silent=not settings.DEBUG):
        from django.template import Context, loader
        from djazz.conf import settings as default_settings
        
        formatters = default_settings['FORMATTERS']
        fmt = self.format or 'default'
        
        if not silent and not fmt in formatters:
            raise self.FormatterUnavailable(fmt)
        
        # Format content
        c = Context({'text': self.content})
        try:
            tpl = loader.get_template(formatters[fmt])
            return tpl.render(c)
        except:
            if silent:
                return ""
            else:
                raise


class PostVarManager(models.Manager):
    VAR_TYPE = None
    
    def get_query_set(self):
        q = super(PostVarManager, self).get_query_set()
        if self.VAR_TYPE:
            q = q.filter(key=self.VAR_TYPE)
        return q

class PostVar(models.Model):
    post    = models.ForeignKey('Post', related_name="postvar")
    key     = models.CharField(max_length=60)
    value   = models.TextField(null=True,blank=True)
    
    objects = PostVarManager()
    
    def __unicode__(self):
        return self.key + " - " + self.post.title

    def save(self, *args, **kwargs):
        if not self.key:
            k = getattr(self.__class__.objects, 'VAR_TYPE')
            self.key = k
        super(PostVar, self).save(*args, **kwargs)

