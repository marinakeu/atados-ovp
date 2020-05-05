from django.test import TestCase

from ovp.apps.uploads.models import UploadedImage

from uuid import UUID


def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except Exception:  # pragma: no cover
        return False

    return str(uuid_obj) == uuid_to_test


class UploadedImageModelTestCase(TestCase):

    def test_str_return_uuid(self):
        """
        Assert that image model __str__ method returns uuid
        """
        img = UploadedImage()
        img.save(object_channel="default")

        uuid = img.__str__()

        self.assertTrue(is_valid_uuid(uuid))
