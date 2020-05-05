from django.conf.urls import url, include
from ovp.apps.catalogue import views

urlpatterns = [
    url(
        r'^catalogue/(?P<slug>[^/]+)/',
        views.CatalogueView.as_view(),
        name='catalogue'
    ),
]
