from django.conf.urls import url, include
from rest_framework import routers

from ovp.apps.faq.views import faq


router = routers.DefaultRouter()
router.register(r'faq', faq.FaqResourceViewSet, 'faq')

urlpatterns = [
    url(r'^', include(router.urls)),
]
