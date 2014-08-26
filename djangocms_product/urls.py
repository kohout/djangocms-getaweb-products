from django.conf.urls import patterns, include, url
from .views import ProductListView, ProductDetailView

urlpatterns = patterns('',
    url(r'^produkt/(?P<slug>[\w-]+)/$',
        ProductDetailView.as_view(),
        name='product-detail'),
    url(r'^$',
        ProductListView.as_view(),
        name='product-index'),
)