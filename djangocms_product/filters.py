# -*- coding: utf-8 -*-
from django.db.models.query_utils import Q
from django_filters import FilterSet, ModelMultipleChoiceFilter
from django_filters.filters import Filter
from djangocms_news.models import NewsItem, NewsCategory
from djangocms_product.models import ProductItem


def product_category(qs, value):
    terms = value.split(',')
    f = None
    for term in terms:
        if f is None:
            f = Q(product_categories__id=term)
        else:
            f = f |\
                Q(product_categories__id=term)

    return qs.filter(f)


class ProductItemFilter(FilterSet):
    category = Filter(action=product_category)

    class Meta:
        model = ProductItem
        fields = ['category']
