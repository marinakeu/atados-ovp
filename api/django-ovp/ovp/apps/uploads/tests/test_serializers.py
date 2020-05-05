from django.test import TestCase
from django.conf import settings

from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory

from ovp.apps.uploads.models import UploadedImage
from ovp.apps.uploads.serializers import UploadedImageSerializer
from django.contrib.auth import get_user_model

from PIL import Image

from tempfile import NamedTemporaryFile


class UploadedImageSerializerTestCase(TestCase):

    def test_image_urls(self):
        """
        Assert that image object returns url
        """
        user = get_user_model().objects.create_user(
            'test_image_urls@test.com',
            'validpassword',
            object_channel="default"
        )

        client = APIClient()
        client.force_authenticate(user=user)

        image = Image.new('RGB', (100, 100))
        tmp_file = NamedTemporaryFile(suffix=".jpg")
        image.save(tmp_file, format="JPEG")
        tmp_file.seek(0)  # otherwise we start reading at the end

        data = {
            'image': tmp_file
        }

        response = client.post(
            reverse('upload-images-list'),
            data,
            format="multipart"
        )

        self.assertTrue(response.status_code == 201)

        img_id = response.data['id']
        img = UploadedImage.objects.get(pk=img_id)

        factory = APIRequestFactory()
        request = factory.post('/')
        serializer = UploadedImageSerializer(
            instance=img,
            context={'request': request}
        )

        media_path = getattr(settings, "MEDIA_URL")
        if media_path == "":
            media_path = "/"

        endpoint = 'http://testserver{media_path}user-uploaded/images'
        test_url = endpoint.format(media_path=media_path)

        self.assertTrue(test_url in serializer.get_image_url(img))
        self.assertTrue(test_url in serializer.get_image_small_url(img))
        self.assertTrue(test_url in serializer.get_image_medium_url(img))
        self.assertTrue(test_url in serializer.get_image_large_url(img))

        self.assertTrue(img.uuid in serializer.get_image_url(img))
        self.assertTrue(img.uuid in serializer.get_image_small_url(img))
        self.assertTrue(img.uuid in serializer.get_image_medium_url(img))
        self.assertTrue(img.uuid in serializer.get_image_large_url(img))
