# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe
from djangocms_product.resolvers import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def productindex_url(context, prefix=None, app_name=None,):
    return reverse(context['request'], prefix, app_name, 'product-index')


@register.simple_tag(takes_context=True)
def productcategory_url(context, get, prefix=None, app_name=None):
    return "%s?category=%s" % (reverse(context['request'], prefix, app_name, 'product-index'), get)


@register.simple_tag(takes_context=True)
def productitem_url(context, slug, prefix=None, app_name=None,):
    return reverse(context['request'], prefix, app_name, 'product-detail', kwargs={
        'slug': slug})


@register.simple_tag(takes_context=True)
def page_pagination(context, category=None, page=1, prefix=None, app_name=None):
    if category:
        return "%s?category=%s&page=%s" % \
               (reverse(context['request'], prefix, app_name, 'product-index'), category, page)
    else:
        return "%s?page=%s" % (reverse(context['request'], prefix, app_name, 'product-index'), page)