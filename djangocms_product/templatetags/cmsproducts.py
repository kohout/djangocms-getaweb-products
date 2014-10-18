# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe
from djangocms_product.resolvers import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def order_url(context, prefix=None, app_name=None,):
    return reverse(context['request'], prefix, app_name, 'order')

@register.simple_tag(takes_context=True)
def basket(context, prefix=None, app_name=None,):
    return reverse(context['request'], prefix, app_name, 'basket')

@register.simple_tag(takes_context=True)
def basket_inc(context, pk, prefix=None, app_name=None,):
    return reverse(context['request'], prefix, app_name, 'basket-increase',
        kwargs={'pk': pk})

@register.simple_tag(takes_context=True)
def basket_dec(context, pk, prefix=None, app_name=None,):
    return reverse(context['request'], prefix, app_name, 'basket-decrease',
        kwargs={'pk': pk})

@register.simple_tag(takes_context=True)
def productindex_url(context, prefix=None, app_name=None,):
    return reverse(context['request'], prefix, app_name, 'product-index')


@register.simple_tag(takes_context=True)
def productcategory_url(context, get, prefix=None, app_name=None):
    return "%s?category=%s" % (reverse(context['request'], prefix, app_name, 'product-index'), get)


@register.simple_tag(takes_context=True)
def productitem_url(context, slug, prefix=None, app_name=None,):
    return reverse(context['request'], prefix, app_name, 'product-detail',
        kwargs={'slug': slug})


@register.simple_tag(takes_context=True)
def page_pagination(context, category=None, page=1, prefix=None, app_name=None):
    if category:
        return "%s?category=%s&page=%s" % \
               (reverse(context['request'], prefix, app_name, 'product-index'), category, page)
    else:
        return "%s?page=%s" % (reverse(context['request'], prefix, app_name, 'product-index'), page)
