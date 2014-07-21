# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe
from djangocms_news.resolvers import reverse

register = template.Library()

def render_img(img):
    return u'<img src="%(url)s" width="%(width)s" height="%(height)s" ' \
        u'title="%(title)s" alt="%(alt)s">' % img

@register.filter()
def image(value, image_format):
    if not value:
        return u''

    return mark_safe(render_img(value._get_image(image_format)))

@register.filter()
def image_url(value, image_format):
    if not value:
        return u''

    return value._get_image(image_format)['url']

@register.simple_tag()
def more_images(news_item, image_format):
    images = news_item.get_more_images()
    return [n._get_image(image_format) for n in images.all()]

@register.simple_tag(takes_context=True)
def newsindex_url(context):
    return reverse(context['request'], 'news-index')

@register.simple_tag(takes_context=True)
def newsitem_url(context, slug):
    return reverse(context['request'], 'news-detail', kwargs={
        'slug': slug})

@register.simple_tag(takes_context=True)
def newscategory_url(context, category_id ):
    return reverse(context['request'], 'news-category', kwargs={
        'category': category_id })
