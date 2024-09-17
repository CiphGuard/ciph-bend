from django.contrib import admin
from django.utils.translation import gettext_lazy as _

ADMIN_TITLE = "CiphraGuard"

admin.site.site_header = _(ADMIN_TITLE)
admin.site.site_title = _(ADMIN_TITLE)
admin.site.index_title = _("Bienvenido a %s" % ADMIN_TITLE)
