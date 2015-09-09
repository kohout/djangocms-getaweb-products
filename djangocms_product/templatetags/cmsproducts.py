# -*- coding: utf-8 -*-
from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag()
def order_url():
    return reverse('cms-product:order')


@register.simple_tag()
def basket():
    return reverse('cms-product:basket')


@register.simple_tag()
def basket_inc(pk):
    return reverse('cms-product:basket-increase', kwargs={'pk': pk})


@register.simple_tag()
def basket_dec(pk):
    return reverse('cms-product:basket-decrease', kwargs={'pk': pk})


@register.simple_tag()
def page_pagination(category=None, page=1):
    if category:
        return "%s?category=%s&page=%s" % \
               (reverse('cms-product:product-index'), category, page)
    else:
        return "%s?page=%s" % (reverse('cms-product:product-index'), page)
