import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from ovp.apps.gallery.models import Gallery
from ovp.apps.organizations.models import Organization
from ovp.apps.projects.models import Project
from ovp.apps.core.models import Post
from ovp.apps.uploads.models import UploadedImage
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


import json


User = get_user_model()


class GalleryViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create(
            email="test1@gmail.com",
            password="test1",
            object_channel="default"
        )
        self.user2 = User.objects.create(
            email="test2@gmail.com",
            password="test1",
            object_channel="default"
        )

        self.img1 = UploadedImage.objects.create(object_channel="default")
        self.img2 = UploadedImage.objects.create(object_channel="default")

    def test_can_create_gallery(self):
        data = {
            "name": "test",
            "description": "abc123",
            "images": [{"id": self.img1.pk}]
        }
        response = self.client.post(
            reverse("gallery-list"),
            data,
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        )
        self.assertEqual(response.status_code, 401)

        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            reverse("gallery-list"),
            data,
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue("uuid" in response.data)
        self.assertEqual(response.data["name"], "test")
        self.assertEqual(response.data["description"], "abc123")
        self.assertEqual(response.data["images"][0]["id"], self.img1.pk)
        self.assertEqual(Gallery.objects.last().owner, self.user1)

    def test_can_edit_gallery(self):
        data = {
            "name": "test2",
            "description": "edited",
            "images": [{"id": self.img2.pk}]
        }
        self.test_can_create_gallery()
        uuid_str = str(Gallery.objects.last().uuid)
        response = self.client.patch(
            reverse("gallery-detail", [uuid_str]),
            data,
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "test2")
        self.assertEqual(response.data["description"], "edited")
        self.assertEqual(response.data["images"][0]["id"], self.img2.pk)
        self.assertEqual(len(response.data["images"]), 1)

        self.client = APIClient()
        response = self.client.patch(
            reverse("gallery-detail", [uuid_str]),
            data,
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        )
        self.assertEqual(response.status_code, 401)

        self.client.force_authenticate(user=self.user2)
        response = self.client.patch(
            reverse("gallery-detail", [uuid_str]),
            data,
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        )
        self.assertEqual(response.status_code, 403)

    def test_can_edit_project_gallery(self):
        # This tests galleries that are
        # associated with a Project.post or Project
        # Other users in the organization should be allowed to edit them
        self.test_can_create_gallery()
        gallery = Gallery.objects.last()
        uuid_str = str(gallery.uuid)

        user1 = User.objects.create(
            email="test-project-owner@gmail.com",
            password="test1",
            object_channel="default"
        )
        user2 = User.objects.create(
            email="test-organization-owner@gmail.com",
            password="test1",
            object_channel="default"
        )
        user3 = User.objects.create(
            email="test-organization-member@gmail.com",
            password="test1",
            object_channel="default"
        )
        org = Organization.objects.create(
            name="test organization",
            owner=user2,
            object_channel="default"
        )
        org.members.add(user3)
        org.save()
        project = Project.objects.create(
            name="test project",
            owner=user1,
            organization=org,
            object_channel="default"
        )

        # With gallery in project
        project.galleries.add(gallery)
        self._test_permissions_multiple_users(user1, user2, user3, uuid_str)

        # With gallery in post
        project.galleries.clear()
        post = Post.objects.create(
            content="tst",
            user=user1,
            gallery=gallery,
            object_channel="default"
        )
        project.posts.add(post)
        self._test_permissions_multiple_users(user1, user2, user3, uuid_str)

        # Without
        project.posts.clear()
        with self.assertRaises(AssertionError):
            self._test_permissions_multiple_users(
                user1,
                user2,
                user3,
                uuid_str
            )

    def _test_permissions_multiple_users(self, project_owner,
                                         organization_owner,
                                         organization_member,
                                         uuid_str):
        data = {
            "name": "test2",
            "description": "edited",
            "images": [{"id": self.img2.pk}]
        }

        # As project owner
        self.client.force_authenticate(user=project_owner)
        response = self.client.patch(
            reverse("gallery-detail", [uuid_str]),
            data,
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        )
        self.assertEqual(response.status_code, 200)

        # As organization owner
        self.client.force_authenticate(user=organization_owner)
        response = self.client.patch(
            reverse("gallery-detail", [uuid_str]),
            data,
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        )
        self.assertEqual(response.status_code, 200)

        # As organization member
        self.client.force_authenticate(user=organization_member)
        response = self.client.patch(
            reverse("gallery-detail", [uuid_str]),
            data,
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        )
        self.assertEqual(response.status_code, 200)

    def test_can_delete_gallery(self):
        self.test_can_create_gallery()
        uuid_str = str(Gallery.objects.last().uuid)
        response = self.client.delete(
            reverse("gallery-detail", [uuid_str]),
            format="json",
            HTTP_X_OVP_CHANNEL="default"
        )
        self.assertEqual(response.status_code, 200)
