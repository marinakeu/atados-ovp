from django.conf.urls import url, include
from ovp.apps.digest import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'digest', views.DigestViewSet, 'digest')


urlpatterns = [
    url(r'^', include(router.urls)),
]
