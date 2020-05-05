from django.conf.urls import url, include
from rest_framework import routers
from ovp.apps.users import views


router = routers.SimpleRouter()
router.register(r'users', views.UserResourceViewSet, 'user')
router.register(
    r'users/recovery-token',
    views.RecoveryTokenViewSet,
    'recovery-token')
router.register(
    r'users/recover-password',
    views.RecoverPasswordViewSet,
    'recover-password')
router.register(
    r'users/request-email-verification',
    views.RequestEmailVerificationViewSet,
    'request-email-verification')
router.register(
    r'users/verificate-email',
    views.VerificateEmailViewSet,
    'email-verification')
router.register(
    r'public-users',
    views.PublicUserResourceViewSet,
    'public-users')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth/', include('ovp.apps.users.auth.oauth2.urls')),
]
