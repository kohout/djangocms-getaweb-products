from menus.base import NavigationNode
from menus.menu_pool import menu_pool
from django.utils.translation import ugettext_lazy as _
from cms.menu_bases import CMSAttachMenu
from .models import ProductCategory

class ProductCategoryMenu(CMSAttachMenu):

    name = _('Product Category Menu')

    def get_nodes(self, request):
        nodes = []
        if not request.current_page:
            return nodes

        for category in ProductCategory.objects.filter(
            productitem__target_page=request.current_page).distinct().order_by(
                'title'):
            node = NavigationNode(
                category.title,
                category.get_absolute_url(),
                category.pk,
                0,
            )
            nodes.append(node)
        return nodes

menu_pool.register_menu(ProductCategoryMenu)
