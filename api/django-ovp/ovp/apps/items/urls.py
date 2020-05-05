from django.conf.urls import url, include
from rest_framework import routers

from ovp.apps.items import views

router = routers.DefaultRouter()
router.register(r'items/images', views.ItemImageViewSet, 'item-images')
router.register(
    r'items/documents',
    views.ItemDocumentViewSet,
    'item-documents')
router.register(r'items', views.ItemViewSet, 'items')

urlpatterns = [
    url(r'^', include(router.urls)),
]
