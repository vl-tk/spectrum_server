from django.urls import path, reverse
from django.utils.translation import gettext as _

from .views import ClientIndexView, clients_viewset


@hooks.register("register_admin_viewset")
def register_viewset():
    return clients_viewset


@hooks.register('register_admin_menu_item')
def register_clients_menu_item():
    return MenuItem(_('Клиенты'), '/cms/clients', icon_name='date', order=151)
