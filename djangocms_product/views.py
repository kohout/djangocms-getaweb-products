# -*- coding: utf-8 -*-
from django.db.models import Q
from django.core.urlresolvers import resolve
from django.views.generic import ListView, DetailView
from .models import ProductItem, ProductCategory

class ProductMixin(object):
    current_category = 0

    def get_queryset(self):
        q = ProductItem.objects.filter(active=True)
        if self.request.user.is_staff or self.request.user.is_superuser:
            # regard public and private version
            q = q.filter(
                Q(target_page=self.request.current_page) |
                Q(target_page=self.request.current_page.publisher_public))
        else:
            # regard only public version
            q = q.filter(target_page=self.request.current_page)

        self.current_category = int(self.kwargs.get('category', 0))
        if self.current_category > 0:
            q = q.filter(product_categories__in=[self.current_category])
        return q

    def get_product_categories(self):
        product_categories = ProductCategory.objects.filter(
            productitem__target_page=self.request.current_page
        ).distinct().order_by('title')
        return [{
            'item': n,
            'count': n.productitem_set.count(),
            'selected': n.id == self.current_category,
        } for n in product_categories]

    def get_context_data(self, *args, **kwargs):
        ctx = super(ProductMixin, self).get_context_data(*args, **kwargs)
        ctx['categories'] = self.get_product_categories()
        return ctx


class ProductListView(ProductMixin, ListView):
    """
    A complete list of the product items
    """
    model = ProductItem
    template_name = 'djangocms_product/list.html'


class ProductDetailView(ProductMixin, DetailView):
    """
    Detail view of a product item
    """
    slug_field = 'slug'
    model = ProductItem
    template_name = 'djangocms_product/detail.html'

    def get_object(self):
        obj = super(ProductDetailView, self).get_object()
        categories = obj.product_categories.all()
        if categories.count() > 0:
            self.current_category = categories[0].id
        return obj

    def get_next(self):
        q = self.get_queryset().filter(
            changed_at__lt=self.object.changed_at).order_by('-changed_at')
        if q.count() > 0:
            return q[0]
        return None

    def get_previous(self):
        q = self.get_queryset().filter(
            changed_at__gt=self.object.changed_at).order_by('changed_at')
        if q.count() > 0:
            return q[0]
        return None

    def get_context_data(self, *args, **kwargs):
        ctx = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        ctx['next'] = self.get_next()
        ctx['previous'] = self.get_previous()
        return ctx
