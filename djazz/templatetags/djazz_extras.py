from django import template

register = template.Library()


@register.filter(name='range')
def filter_range(value, arg="0, 1"):
    arg = str(arg)
    start = 0
    stop = int(value)
    step = 1
    
    args = arg.split(',')
    args.reverse()
    
    if len(args) > 0:
        start = int(args.pop().strip())
    
    if len(args) > 0:
        step = int(args.pop().strip())
    
    return range(start, stop, step)


@register.filter(name='indexof')
def filter_index(index, tab):
    try:
        return tab[index]
    except:
        return None

@register.filter(name='attrof')
def filter_attr(attr, obj):
    return getattr(obj, attr, None)



def render_include_once(self, context):
    ctname = '_include_once_node_registry'
    if not ctname in context:
        context[ctname] = {}
    
    if not self.include_path or self.include_path in context[ctname]:
        return ""
    else:
        context[ctname][self.include_path] = True
        return self._render_origin(context)


@register.tag(name='include_once')
def do_include_once(parser, token):
    import types
    from django.template.loader_tags import (do_include,
                                             ConstantIncludeNode,
                                             IncludeNode)
    included = do_include(parser, token)
    
    if isinstance(included, ConstantIncludeNode):
        try:
            included.include_path = included.template.name
        except:
            included.include_path = None
    elif isinstance(included, IncludeNode):
        included.include_path = included.template_name
    else:
        included.include_path = None
    
    included._render_origin = included.render
    included.render = types.MethodType(render_include_once, included)
    return included


def render_ssi_once(self, context):
    ctname = '_ssi_once_node_registry'
    if not ctname in context:
        context[ctname] = {}
    
    path = str(self.filepath)
    if path[0] in ['"',"'"] and path[0] == path[-1]:
        path = path[1:-1]
    
    if path in context[ctname]:
        return ""
    else:
        context[ctname][path] = True
        return self._render_origin(context)

@register.tag(name='ssi_once')
def do_ssi_once(parser, token):
    
    import types
    from django.template.defaulttags import ssi
    node = ssi(parser, token)
    node._render_origin = node.render
    node.render = types.MethodType(render_ssi_once, node)
    return node
