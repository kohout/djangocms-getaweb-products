from django.core.urlresolvers import resolve, reverse as _reverse

def reverse(request, viewname, kwargs={}):
    _namespace = resolve(request.path).namespace
    return _reverse(u':'.join([_namespace, viewname]), kwargs=kwargs)
