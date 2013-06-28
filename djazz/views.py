from django.db import models
from django.http import HttpResponse, Http404
import datetime, json


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return super(JSONEncoder, self).default(obj)


class JsonRestView(object):
    
    def __init__(self, model, http404=Http404,
                              fields=None):
        
        if not issubclass(model, models.Model):
            raise Exception('model is not a Model subclass')
        self.model = model
        self.http404 = http404
        self.fields = fields
    
    
    @property
    def urls(self):
        from django.conf.urls import url, patterns
        
        urlpatterns = patterns('',
            url('^$',self.model_view,name='list'),
            url('^$',self.model_view,name='post'),
            url('^(?P<model_id>\d+)/$',self.model_view,name='get'),
            url('^(?P<model_id>\d+)/$',self.model_view,name='put'),
            url('^(?P<model_id>\d+)/$',self.model_view,name='delete'),
        )
        return urlpatterns
    
    
    def get_response(self, data=''):
        return HttpResponse(data, content_type="application/json")
    
    
    def serialize_queryset(self, queryset, fields=None):
        datas = []
        for model in queryset:
            datas.append(self.serialize_model(model, fields))
        return json.dumps(datas, cls=JSONEncoder)
    
    
    def serialize_model(self, model, fields=None):
        data = {}
        fields = fields or self.model._meta.get_all_field_names()
        for field in fields:
            data[field] = getattr(model, field)
        return data
    
    
    def decode_model(self, datas):
        return self.model(**datas)
    
    
    def model_view(self, request, model_id=None):
        
        method = request.method
        if not model_id and method == 'GET':
            return self.get_models(request)
        elif not model_id and method == 'POST':
            return self.post_model(request)
        elif method == 'GET':
            return self.get_model(request, model_id)
        elif method == 'PUT':
            return self.put_model(request, model_id)
        elif method == 'DELETE':
            return self.delete_model(request, model_id)
        else:
            raise self.http404('Page not found')
    
    # list
    def get_models(self, request):
        options = {
            'results': 20,
            'offset': 0
        }
        options.update(request.GET)
        
        q = self.model.objects.all()
        q = q[options['offset']:options['results']]
        
        data = self.serialize_queryset(q)
        
        response = self.get_response(data)
        return response
    
    # create
    def post_model(self, request):
        datas = json.loads(request.read())
        model = self.decode_model(datas)
        model.save()
        return self.get_response(self.serialize_model(model))
    
    # view
    def get_model(self, request, model_id):
        from django.shortcuts import get_object_or_404
        model = get_object_or_404(self.model, pk=model_id)
        return self.get_response(self.serialize_model(model))
    
    # update
    def put_model(self, request, model_id):
        datas = json.loads(request.read())
        model = self.decode_model(datas)
        model.save()
        return self.get_response(self.serialize_model(model))
    
    # delete
    def delete_model(self, request, model_id):
        from django.shortcuts import get_object_or_404
        model = get_object_or_404(self.model, pk=model_id)
        model.delete()
        return self.get_response(self.serialize_model(model))
    