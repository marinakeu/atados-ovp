from django.contrib.admin import AdminSite
from django.views.decorators.cache import never_cache
from .forms import ChannelAdminAuthenticationForm


class ChannelAdminSite(AdminSite):
    login_form = ChannelAdminAuthenticationForm

    @never_cache
    def login(self, request, channel_slug=None, extra_context=None):
        return super().login(request, extra_context)


admin_site = ChannelAdminSite(name='channeladmin')
