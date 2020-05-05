import os
from io import BytesIO
from tempfile import TemporaryFile
from django.core.files import uploadedfile
from django.core.files.base import ContentFile
from django.conf import settings

from PIL import Image


# GCS is actually the default ovp's bucket, so, lets try to optimize for it
# As images *never* changes urls, we can concat domain,
# bucket and url to obtain a full qualified
# absolute uri, preventing a #get_blog for each image

def build_absolute_uri(req, image):
    try:
        if hasattr(settings, 'GCS_BUCKET'):
            return image.url
        return req.build_absolute_uri(image.url) if image else None
    except ValueError:
        return None


def perform_image_crop(image_obj, crop_rect=None):
    img_ext = os.path.splitext(image_obj.name)[1][1:].upper()
    img_ext = 'JPEG' if img_ext == 'JPG' else img_ext
    if crop_rect is None:
        return image_obj

    image = BytesIO(image_obj.read())

    base_image = Image.open(image)
    tmp_img, tmp_file = base_image.crop(crop_rect), BytesIO()
    tmp_img.save(tmp_file, format=img_ext)

    tmp_file = ContentFile(tmp_file.getvalue())
    return uploadedfile.InMemoryUploadedFile(
        tmp_file,
        None,
        image_obj.name,
        image_obj.content_type,
        tmp_file.tell,
        None
    )
