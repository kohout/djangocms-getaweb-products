# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import resolve, reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.template.context import Context
from django.template.loader import get_template
from django.views.generic import View, ListView, DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from djangocms_product.filters import ProductItemFilter
from .models import ProductItem, ProductCategory, Order, OrderedItem
from .forms import OrderForm
import json
from decimal import Decimal as D

def my_import(name):
    components = name.split('.')
    method = components.pop()
    mod = __import__('.'.join(components))
    return getattr(mod, method)

def get_shipping(basket, products, total_amount):
    shipping = {}
    try:
        from settings import DJANGOCMS_PRODUCT_SHIPPING
        for shipping_method_string in DJANGOCMS_PRODUCT_SHIPPING:
            shipping_method = my_import(shipping_method_string)
            shipping.update(shipping_method(basket, products, total_amount))
    except ImportError:
        pass
    return shipping

class SimpleOrderSuccessView(TemplateView):
    template_name = 'djangocms_product/order_success.html'


class SimpleOrderView(CreateView):
    model = Order
    form_class = OrderForm

    def get_basket(self):
        return self.request.session.get('basket', {})

    def form_valid(self, form):
        self.object = form.save()

        # 2. save basket
        basket = self.get_basket()
        total_amount = 0
        products = []
        for key in basket.keys():
            try:
                amount = basket[key]
            except KeyError:
                amount = 0
            if amount > 0:
                oi = OrderedItem()
                oi.order = self.object
                oi.amount = amount
                oi.product_item = ProductItem.objects.get(pk=int(key))
                products.append(oi.product_item)
                total_amount += oi.product_item.price * oi.amount
                print "order_id", oi.order
                print "product_item_id", oi.product_item.pk
                oi.save()

        # 3. add cumulated info
        self.object.total_amount = total_amount
        shipping = get_shipping(basket, products, total_amount)
        if shipping:
            shipping = shipping.get(self.object.country, None)
            if shipping:
                self.object.shipping_amount = shipping['value']
                self.object.shipping_label = shipping['label']
        self.object.save()

        # 4. reset basket
        self.request.session['basket'] = {}

        # 5. send notification mail
        for to in ['ck@getaweb.at']:
            send_mail('schullerwein.at - Bestellbestätigung',
                'Es wurde eine neue Bestell-Anfrage erstellt:\nhttp://%s%s' % (
                    self.request.META['HTTP_HOST'],
                    reverse('admin:djangocms_product_order_change', args=[
                        self.object.pk]),
                ),
                'schullerwein@getaweb.at',
                [to], fail_silently=False)

        # 5. send email to buyer
        ctx = Context({
            'object': self.object,
            'products': OrderedItem.objects.filter(order=self.object),
        })
        from django.core.mail import EmailMultiAlternatives

        subject = 'schullerwein.at - Danke für Ihre Bestellung!'
        from_email = 'schullerwein@getaweb.at'
        to = self.object.email

        text_content = get_template('djangocms_product/email.txt').render(ctx)
        html_content = get_template('djangocms_product/email.html').render(ctx)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return super(SimpleOrderView, self).form_valid(form)

    def get_success_url(self):
        view_name = '%s-product:order-success' % (
            settings.SITE_PREFIX, )
        return reverse(view_name)

    def get_context_data(self, *args, **kwargs):
        ctx = super(SimpleOrderView, self).get_context_data(*args, **kwargs)
        ctx['products'] = []
        basket = self.get_basket()
        products = ProductItem.objects.filter(pk__in=basket.keys())
        total_amount = D('0.00')
        for product in products:
            try:
                amount = basket[unicode(product.pk)]
            except KeyError:
                amount = 0
            if amount > 0:
                total = amount * product.price
                total_amount += total
                ctx['products'].append({
                    'item': product,
                    'amount': amount,
                    'total': total,
                })
        ctx['total_amount'] = total_amount
        ctx['shipping'] = get_shipping(basket, products, total_amount)
        return ctx

class BasketChangeMixin(object):
    model = ProductItem
    basket = None

    def get_basket(self):
        self.basket = self.request.session.get('basket', {})

    def set_basket(self):
        self.request.session['basket'] = self.basket

    def change_basket(self):
        pass

    def get(self, request, *args, **kwargs):
        if hasattr(self, 'get_object'):
            self.object = self.get_object()
        self.get_basket()
        self.change_basket()
        self.set_basket()
        view_name = '%s-product:product-index' % (
            settings.SITE_PREFIX, )
        if request.is_ajax:
            return HttpResponse(json.dumps(self.basket),
                content_type="application/json")
        else:
            return HttpResponseRedirect(reverse(view_name))


class BasketView(BasketChangeMixin, View):
    pass


class BasketIncreaseView(BasketChangeMixin, DetailView):

    def change_basket(self):
        key = unicode(self.object.pk)
        try:
            self.basket[key] = self.basket[key] + 1
        except KeyError:
            self.basket[key] = 1


class BasketDecreaseView(BasketChangeMixin, DetailView):

    def change_basket(self):
        key = unicode(self.object.pk)
        try:
            self.basket[key] = max(self.basket[key] - 1, 0)
        except KeyError:
            self.basket[key] = 0


class ProductMixin(object):
    current_category = 0
    current_page = None

    def get_current_page(self):
        if self.current_page:
            return self.current_page
        self.current_page = self.request.current_page
        if self.current_page.publisher_is_draft:
            self.current_page = self.current_page.publisher_public
        return self.current_page

    def get_queryset(self):
        q = ProductItem.objects.filter(active=True)
        q = q.filter(target_page=self.get_current_page())
        return q

    def get_product_categories(self):
        product_categories = ProductCategory.objects.filter(
            productitem__target_page=self.get_current_page()
        ).distinct().order_by('section', 'order', 'title')
        return product_categories
        #return [{
        #    'item': n,
        #    'count': n.productitem_set.count(),
        #    'selected': n.id == self.current_category,
        #    'order': n.order,
        #    'section': n.section,
        #} for n in product_categories]

    def get_context_data(self, *args, **kwargs):
        ctx = super(ProductMixin, self).get_context_data(*args, **kwargs)
        ctx['categories'] = self.get_product_categories()
        if 'category' in self.kwargs:
            ctx['category'] = self.kwargs['category']
        return ctx


class ProductListView(ProductMixin, ListView):
    """
    A complete list of the product items
    """
    model = ProductItem
    template_name = 'djangocms_product/list.html'
    paginate_by = 25
    filter_class = ProductItemFilter

    def get_queryset(self):
        q = super(ProductListView, self).get_queryset()
        return self.filter_class(self.request.GET, q)

    def get_context_data(self, *args, **kwargs):
        ctx = super(ProductListView, self).get_context_data(*args, **kwargs)
        if self.request.GET.get('category'):
            filter_categories = self.request.GET.get('category')
            filter_categories = filter_categories.split(',')
            ctx['filter_categories'] = filter_categories
        else:
            ctx['show_all'] = True
        return ctx


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
