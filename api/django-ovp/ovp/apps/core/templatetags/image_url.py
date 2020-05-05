from django.conf import settings
from django import template
from ovp.apps.uploads.serializers import UploadedImageSerializer

def image_url(obj, prefix=""):
    if not obj:
        return ""

    if obj.absolute:
        return obj.image.name if obj.image else ""

    return prefix + obj.image.url if obj.image else ""

register = template.Library()
register.filter('image_url', image_url)
