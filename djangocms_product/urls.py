from django.conf.urls import patterns, include, url
from .views import (ProductListView, ProductDetailView,
    SimpleOrderView, SimpleOrderSuccessView,
    BasketView, BasketIncreaseView, BasketDecreaseView)
from django.conf import settings

urlpatterns = patterns('',
    url(r'^produkt/(?P<slug>[\w-]+)/$',
        ProductDetailView.as_view(),
        name='product-detail'),
    url(r'^$',
        ProductListView.as_view(),
        name='product-index'),
)

if getattr(settings, 'DJANGOCMS_PRODUCT_SIMPLEORDER', False):
    urlpatterns += patterns('',
        url(r'^order/$',
            SimpleOrderView.as_view(),
            name='order'),
        url(r'^order/success/$',
            SimpleOrderSuccessView.as_view(),
            name='order-success'),
        url(r'^basket/$',
            BasketView.as_view(),
            name='basket'),
        url(r'^basket/inc/(?P<pk>[\w-]+)/$',
            BasketIncreaseView.as_view(),
            name='basket-increase'),
        url(r'^basket/dec/(?P<pk>[\w-]+)/$',
            BasketDecreaseView.as_view(),
            name='basket-decrease'),
    )
