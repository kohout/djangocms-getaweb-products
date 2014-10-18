from menus.base import NavigationNode
from menus.menu_pool import menu_pool
from django.utils.translation import ugettext_lazy as _
from cms.menu_bases import CMSAttachMenu
from .models import ProductCategory


class ProductCategoryMenu(CMSAttachMenu):
    name = _('Product Category Menu')
    current_page = None

    def get_current_page(self, request):
        if self.current_page:
            return self.current_page
        self.current_page = request.current_page
        if self.current_page.publisher_is_draft:
            self.current_page = self.current_page.publisher_public
        return self.current_page

    def get_nodes(self, request):
        nodes = []
        if not request.current_page:
            return nodes

        for category in ProductCategory.objects.filter(
            productitem__target_page=self.get_current_page(request)
        ).distinct().order_by(
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
