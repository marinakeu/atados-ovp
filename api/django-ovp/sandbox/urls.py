from django.conf.urls import url, include
from ovp.apps.channels.admin import admin_site

import ovp.apps.core.urls
import ovp.apps.uploads.urls
import ovp.apps.users.urls
import ovp.apps.projects.urls
import ovp.apps.organizations.urls
import ovp.apps.search.urls
import ovp.apps.faq.urls
import ovp.apps.catalogue.urls
import ovp.apps.items.urls
import ovp.apps.ratings.urls
import ovp.apps.gallery.urls
import ovp.apps.donations.urls
import ovp.apps.digest.urls

core_urls = [
    # Core
    url(r'^', include(ovp.apps.core.urls)),

    # Uploads
    url(r'^', include(ovp.apps.uploads.urls)),

    # Users
    url(r'^', include(ovp.apps.users.urls)),

    # Projects
    url(r'^', include(ovp.apps.projects.urls)),

    # Organizations
    url(r'^', include(ovp.apps.organizations.urls)),

    # Search
    url(r'^', include(ovp.apps.search.urls)),

    # FAQ
    url(r'^', include(ovp.apps.faq.urls)),

    # Catalogue
    url(r'^', include(ovp.apps.catalogue.urls)),

    # Items
    url(r'^', include(ovp.apps.items.urls)),

    # Ratings
    url(r'^', include(ovp.apps.ratings.urls)),

    # Gallery
    url(r'^', include(ovp.apps.gallery.urls)),

    # Donations
    url(r'^', include(ovp.apps.donations.urls)),

    # Digest
    url(r'^', include(ovp.apps.digest.urls)),
]

urlpatterns = [
    # Admin
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    url(r'^martor/', include('martor.urls')),
    url(r'^admin/', admin_site.urls),
] + core_urls
