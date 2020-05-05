from django.conf.urls import url, include
from rest_framework import routers

from ovp.apps.uploads import views


router = routers.DefaultRouter()
router.register(r'uploads/images', views.UploadedImageViewSet, 'upload-images')
router.register(
    r'uploads/documents', views.UploadedDocumentViewSet, 'upload-documents'
)


urlpatterns = [
    url(r'^', include(router.urls)),
]
