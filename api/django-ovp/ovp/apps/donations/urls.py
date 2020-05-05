from django.conf.urls import url, include

from rest_framework import routers

from ovp.apps.donations.views import DonationViewSet

donations = routers.SimpleRouter()
donations.register(r'donations', DonationViewSet, 'donation')

urlpatterns = [
    url(r'^', include(donations.urls)),
]
