from django.core.urlresolvers import resolve, reverse as _reverse


def reverse(request, prefix, app_name, view_name, kwargs={}):
    _namespace = resolve(request.path).namespace
    if prefix is not None and app_name is not None:
        _namespace = prefix + '-' + app_name
    return _reverse(u':'.join([_namespace, view_name]), kwargs=kwargs)
