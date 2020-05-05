from django.test import TestCase

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from django.http.request import QueryDict
from django.contrib.auth import get_user_model

from PIL import Image

from tempfile import NamedTemporaryFile

import json


class UploadedImageViewSetTestCase(TestCase):
    def test_cant_upload_unauthenticated(self):
        """
        Assert that it's not possible to upload
        while unauthenticated without custom header
        """
        client = APIClient()
        response = client.post(
            reverse('upload-images-list'),
            {},
            format="multipart"
        )

        self.assertTrue(response.status_code == 401)

    def test_cant_upload_no_image(self):
        """
        Assert that error is raised on no image
        """
        user = get_user_model().objects.create_user(
            'test_cant_upload_no_image@test.com',
            'validpassword',
            object_channel="default"
        )

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(
            reverse('upload-images-list'),
            {},
            format="multipart"
        )

        self.assertTrue(response.status_code == 400)
        self.assertTrue(response.data['image'][0] == 'No file was submitted.')

    def test_can_upload_authenticated(self):
        """
        Assert that it's possible to upload while authenticated
        """
        user = get_user_model().objects.create_user(
            'test_can_upload@test.com',
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

    def test_can_upload_unauthenticated_with_header(self):
        """
        Assert that it's possible to upload while
        unauthenticated if sent correct header
        """
        client = APIClient()

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
            format="multipart",
            HTTP_X_UNAUTHENTICATED_UPLOAD=True
        )

        data = json.loads(response.content.decode('utf-8'))

        self.assertTrue(response.status_code == 201)
