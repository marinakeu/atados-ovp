from django.conf.urls import url, include
from rest_framework import routers

from ovp.apps.gallery import views


router = routers.DefaultRouter()
router.register(r'gallery', views.GalleryResourceViewSet, 'gallery')


urlpatterns = [
    url(r'^', include(router.urls)),
]
