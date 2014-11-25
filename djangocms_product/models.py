# -*- coding: utf-8 -*-
from cms.models.pluginmodel import CMSPlugin
from cms.models.pagemodel import Page
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _
from django.utils.timezone import utc
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.exceptions import InvalidImageFormatError
from tinymce.models import HTMLField
from decimal import Decimal
import datetime
import settings

DJANGOCMS_PRODUCT_DEFAULT_COUNTRY = getattr(settings,
    'DJANGOCMS_PRODUCT_DEFAULT_COUNTRY', u'')

DJANGOCMS_PRODUCT_COUNTRIES = getattr(settings,
    'DJANGOCMS_PRODUCT_COUNTRIES', [])

class ProductCategory(models.Model):
    title = models.CharField(
        max_length=150,
        verbose_name=_(u'Title'))

    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_(u'Order'))

    section = models.CharField(
        max_length=50,
        blank=True, default=u'',
        verbose_name=_(u'Section'))

    slug = models.SlugField(
        max_length=255,
        db_index=True,
        unique=True,
        verbose_name=_("slug"))

    free_shipping = models.BooleanField(
        default=False,
        help_text=u'Für Produkte dieser Kategorie werden keine ' \
            u'Versandkosten berechnet',
        verbose_name=u'Versandkostenfrei')

    def active_productitems(self):
        return self.productitem_set.filter(active=True)

    def productitems_count(self):
        return self.active_productitems().count()

    productitems_count.short_description = _(u'Count of active product items')

    def get_absolute_url(self):
        view_name = '%s-product:product-index' % (
            settings.SITE_PREFIX, )
        return "%s?category=%s" % (reverse(view_name), self.pk)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _(u'Product Category')
        verbose_name_plural = _(u'Product Categories')


class ProductItem(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_(u'Created at'))

    changed_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_(u'Created at'))

    active = models.BooleanField(
        default=False,
        verbose_name=_(u'Active'))

    title = models.CharField(
        max_length=150,
        verbose_name=_(u'Headline of the product article'))

    slug = models.SlugField(
        max_length=255,
        db_index=True,
        unique=True,
        verbose_name=_("slug"))

    content = HTMLField(
        blank=True,
        verbose_name=_(u'Content'))

    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_(u'Price'))

    special_offer = models.CharField(
        max_length=255,
        blank=True, null=True,
        verbose_name=_(u'Special offer'))

    product_categories = models.ManyToManyField(
        ProductCategory,
        blank=True, null=True,
        verbose_name=_(u'Selected product categories'))

    target_page = models.ManyToManyField(
        Page,
        blank=True, null=True,
        verbose_name=_(u'Target Page'))

    document = models.FileField(
        upload_to='cms_products',
        blank=True, null=True,
        verbose_name=_(u'Document (e.g. product catalogue, ...)'))

    link = models.URLField(
        blank=True, null=True,
        help_text=_(u'Link to more detailed page'),
        verbose_name=_(u'URL'))

    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_(u'Order'))

    out_of_stock = models.BooleanField(
        default=False,
        verbose_name=u'ausverkauft')

    def get_first_image(self):
        images = self.productimage_set.all()
        if images.count() == 0:
            return None
        first_image = images[0]
        return first_image

    def get_more_images(self):
        return self.productimage_set.all()[1:]

    def has_multiple_images(self):
        return self.productimage_set.count() > 1

    def get_absolute_url(self):
        view_name = '%s:product-detail' % (
            self.target_page.application_namespace, )
        return reverse(view_name, kwargs={'slug': self.slug})

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('-changed_at', )
        verbose_name = _(u'Product Item')
        verbose_name_plural = _(u'Product Items')


class ProductTeaser(CMSPlugin):
    product_ORDERING_FUTURE_ASC = 'future_asc'
    product_ORDERING_PAST_DESC = 'past_desc'

    product_ORDERING_CHOICES = (
        (product_ORDERING_FUTURE_ASC, _(u'from now to future (ascending)')),
        (product_ORDERING_PAST_DESC, _(u'from now to past (descending)')),
    )
    title = models.CharField(
        max_length=150,
        verbose_name=_(u'Headline of the product list'))

    product_categories = models.ManyToManyField(
        ProductCategory,
        verbose_name=_(u'Selected product categories'))

    ordering = models.CharField(
        max_length=20,
        choices=product_ORDERING_CHOICES,
        default=product_ORDERING_PAST_DESC,
        verbose_name=_(u'Ordering/Selection of Articles'))

    target_page = models.ForeignKey(Page,
        verbose_name=_(u'Target Page'))

    def get_items(self):
        items = ProductItem.objects.filter(active=True)
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        if self.ordering == self.product_ORDERING_PAST_DESC:
            items = items.filter(changed_at__lte=now).order_by('-changed_at')
        else:
            items = items.filter(changed_at__gte=now).order_by('changed_at')
        return items

    def __unicode__(self):
        return self.title


class ProductImage(models.Model):
    image = ThumbnailerImageField(
        upload_to='cms_product/',
        verbose_name=_(u'Image'))

    image_width = models.PositiveSmallIntegerField(
        default=0,
        null=True,
        verbose_name=_(u'Original Image Width'))

    image_height = models.PositiveSmallIntegerField(
        default=0,
        null=True,
        verbose_name=_(u'Original Image Height'))

    title = models.CharField(
        blank=True,
        default='',
        max_length=150,
        verbose_name=_(u'Image Title'))

    alt = models.CharField(
        blank=True,
        default='',
        max_length=150,
        verbose_name=_(u'Alternative Image Text'))

    ordering = models.PositiveIntegerField(
        verbose_name=_(u'Ordering'))

    product_item = models.ForeignKey(ProductItem,
        verbose_name=_(u'Product Item'))

    def get_title(self):
        if self.title:
            return self.title
        return self.product_item.title

    def get_alt(self):
        if self.alt:
            return self.alt
        return u'Bild %s' % (self.ordering + 1)

    def save(self, *args, **kwargs):
        if self.ordering is None:
            self.ordering = self.product_item.productimage_set.count()
        super(ProductImage, self).save(*args, **kwargs)

    def _get_image(self, image_format):
        _image_format = settings.THUMBNAIL_ALIASES[''][image_format]
        _img = self.image
        try:
            img = get_thumbnailer(_img).get_thumbnail(_image_format)
            return {
                'url': img.url,
                'width': img.width,
                'height': img.height,
                'alt': self.alt,
                'title': self.title,
            }
        except (UnicodeEncodeError, InvalidImageFormatError):
            return None

    def get_preview(self):
        return self._get_image('preview')

    def get_teaser(self):
        return self._get_image('teaser')

    def get_normal(self):
        return self._get_image('normal')

    def get_main(self):
        return self._get_image('main')

    def get_fullsize(self):
        return self._get_image('fullsize')

    def __unicode__(self):
        if self.title:
            return self.title
        if self.alt:
            return self.alt
        return _(u'Image #%s') % self.ordering

    class Meta:
        ordering = ['ordering']
        verbose_name = _(u'Product Image')
        verbose_name_plural = _(u'Product Images')

class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,
        verbose_name=_(u'Erstellt am'))
    first_name = models.CharField(max_length=50,
        verbose_name=_(u'Vorname'))
    last_name = models.CharField(max_length=50,
        verbose_name=_(u'Nachname'))
    address = models.CharField(max_length=150,
        verbose_name=_(u'Adresse'))
    zipcode = models.CharField(max_length=5,
        verbose_name=_(u'PLZ'))
    city = models.CharField(max_length=50,
        verbose_name=_(u'Ort'))
    country = models.CharField(max_length=100,
        blank=True,
        default=DJANGOCMS_PRODUCT_DEFAULT_COUNTRY,
        choices=DJANGOCMS_PRODUCT_COUNTRIES,
        verbose_name=_(u'Land'))
    telephone = models.CharField(max_length=50,
        verbose_name=_(u'Telefon'))
    email = models.EmailField(max_length=150,
        verbose_name=_(u'Email'))
    total_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_(u'Gesamtbetrag'))
    shipping_amount = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_(u'Versandkosten'))
    shipping_label = models.CharField(max_length=150,
        default=u'', blank=True,
        verbose_name=_(u'Versand-Label'))

    @property
    def amount_with_shipping(self):
        return self.total_amount + self.shipping_amount

    class Meta:
        verbose_name = _(u'Bestellung')
        verbose_name_plural = _(u'Bestellungen')

class OrderedItem(models.Model):
    order = models.ForeignKey(Order,
        verbose_name=_(u'Bestellung'))
    product_item = models.ForeignKey(ProductItem,
        verbose_name=_(u'Bestelltes Produkt'))
    amount = models.PositiveIntegerField(default=0,
        verbose_name=_(u'Menge'))
