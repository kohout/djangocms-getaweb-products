# -*- coding: utf-8 -*-
from haystack import indexes
from .models import NewsItem


class NewsItemIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title', null=True)
    url = indexes.CharField(model_attr='get_absolute_url', null=True)
    target_page = indexes.IntegerField(model_attr='target_page__id', null=True)

    def get_model(self):
        return NewsItem

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(active=True)
