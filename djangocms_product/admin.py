# -*- coding: utf-8 -*-
from adminsortable.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.utils.translation import ugettext as _
from .models import ProductCategory, ProductItem, ProductImage
from .forms import ProductItemForm


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'productitems_count', )
    search_fields = ('title', )
    prepopulated_fields = {'slug': ('title',)}


class ProductImageInline(SortableInlineAdminMixin,
			 admin.TabularInline):
    fields = ('render_preview', 'image', 'title', 'alt', 'ordering')
    readonly_fields = ('render_preview', )
    model = ProductImage
    extra = 0
    sortable_field_name = 'ordering'

    def render_preview(self, product_image):
        url = product_image.image['preview'].url
        if url:
            return u'<img src="%s">' % url
        else:
            return u''

    render_preview.allow_tags = True
    render_preview.short_description = _(u'Preview')


class ProductItemAdmin(admin.ModelAdmin):
    form = ProductItemForm
    list_display = ('render_preview',
		    'title',
		    'list_of_product_categories',
		    'price',
		    'special_offer',
                    'active', )
    list_display_links = ('render_preview', 'title', 'price', )
    readonly_fields = ('render_preview', )
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content', )
    fieldsets = (
        (_(u'Common'), {
            'fields': (
                ('active', ),
                ('price', 'special_offer', ),
                ('product_categories', 'target_page'),
            )
        }),
        (_(u'Content'), {
            'fields': (
		('title', 'slug', ),
		('content', ),
            ),
        }),
        (_(u'External Content'), {
            'fields': (
                ('document', 'link', ),
            ),
        })
    )
    inlines = [ProductImageInline]

    #raw_id_fields = ('product_categories', )
    #autocomplete_lookup_fields = {
    #    'm2m': ['product_categories'],
    #}

    def render_preview(self, product_item):
        product_image = product_item.get_first_image()
        if not product_image:
            return u''

        url = product_image.image['preview'].url
        if not url:
            return u''

        return u'<img src="%s">' % url

    render_preview.allow_tags = True
    render_preview.short_description = _(u'Preview')

    def list_of_product_categories(self, product_item):
        return u', '.join([n.title for n in
            product_item.product_categories.all()])

    list_of_product_categories.short_description = _(u'Categories')

admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(ProductItem, ProductItemAdmin)
