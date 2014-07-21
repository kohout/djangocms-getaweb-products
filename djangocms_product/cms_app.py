from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _
from .menu import ProductCategoryMenu

class ProductApp(CMSApp):
    name = _('Product Module')
    urls = ['djangocms_product.urls']
    app_name = 'cmsproduct'
    menus = [ProductCategoryMenu]

apphook_pool.register(ProductApp)
