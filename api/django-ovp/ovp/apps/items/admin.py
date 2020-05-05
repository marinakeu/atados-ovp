from ovp.apps.channels.admin import admin_site
from ovp.apps.items.models import Item, ItemImage, ItemDocument

admin_site.register(Item)
admin_site.register(ItemImage)
admin_site.register(ItemDocument)