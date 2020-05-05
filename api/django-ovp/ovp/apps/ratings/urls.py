from django.conf.urls import url, include
from rest_framework import routers

from ovp.apps.ratings import views

router = routers.SimpleRouter()
router.register(
    r'ratings',
    views.RatingRequestResourceViewSet,
    'rating-request'
)


urlpatterns = [
    url(r'^', include(router.urls)),
]
