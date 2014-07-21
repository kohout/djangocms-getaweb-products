from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from .models import ProductTeaser

class ProductTeaserPlugin(CMSPluginBase):
    model = ProductTeaser
    name = _("Product Teaser")
    render_template = "cms/plugins/product/teaser.html"

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        context['items'] = instance.get_items()
        return context

plugin_pool.register_plugin(ProductTeaserPlugin)
