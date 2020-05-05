import dateutil.parser
from django.test import TestCase
from django.test import override_settings

from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp.apps.core.helpers.tests import result_contains
from ovp.apps.projects.models import Project
from ovp.apps.projects.models import VolunteerRole
from ovp.apps.projects.models import Category
from ovp.apps.users.models import User
from ovp.apps.organizations.models import Organization
from ovp.apps.gallery.models import Gallery
from ovp.apps.core.models import Post
from ovp.apps.core.models import Cause
from ovp.apps.core.models import Skill
from ovp.apps.channels.models import Channel
from ovp.apps.uploads.models import UploadedDocument

from ovp.apps.channels.models.channel_setting import ChannelSetting

from collections import OrderedDict

import pytz
import copy


base_project = {
    "name": "test project",
    "slug": "test-cant-override-slug-on-creation",
    "details": "this is just a test project",
    "description": "the project is being tested",
    "minimum_age": 18,
    "address": {
        "typed_address": "r. tecainda, 81, sao paulo"
    },
    "disponibility": {
        "type": "work",
        "work": {
            "description": "abc"
        }
    },
    "causes": [
        {
            "id": 1
        },
        {
            "id": 2
        }
    ],
    "skills": [
        {
            "id": 3
        },
        {
            "id": 4
        }
    ]
}


class ProjectResourceViewSetTestCase(TestCase):
    def setUp(self):
        ChannelSetting.objects.create(
            key="CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION",
            value="1",
            object_channel="default"
        )
        cache.clear()

    def test_cant_create_project_unauthenticated(self):
        """
        Assert that it's not possible to create a project while unauthenticated
        """
        client = APIClient()
        response = client.post(reverse("project-list"), {}, format="json")

        self.assertTrue(
            response.data["detail"]
            == "Authentication credentials were not provided."
        )
        self.assertTrue(response.status_code == 401)

    def test_can_create_project(self):
        """
        Assert that it's possible to create a project while authenticated
        """
        user = User.objects.create_user(
            email="test_can_create_project@gmail.com",
            password="testcancreate",
            object_channel="default"
        )

        data = copy.deepcopy(base_project)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(reverse("project-list"), data, format="json")

        self.assertTrue(response.status_code == 201)
        self.assertTrue(response.data["id"])
        self.assertTrue(response.data["name"] == data["name"])
        self.assertTrue(response.data["slug"] == "test-project")
        self.assertTrue(response.data["details"] == data["details"])
        self.assertTrue(response.data["description"] == data["description"])
        self.assertTrue(response.data["minimum_age"] == data["minimum_age"])
        self.assertTrue(len(response.data["causes"]) == 2)
        self.assertTrue(len(response.data["skills"]) == 2)

        project = Project.objects.get(pk=response.data["id"])
        self.assertTrue(project.owner.id == user.id)
        self.assertTrue(
            project.address.typed_address == data["address"]["typed_address"]
        )

    def test_cant_create_project_empty_name(self):
        """
        Assert that it's not possible to create a project with empty name
        """
        user = User.objects.create_user(
            email="test_can_create_project@gmail.com",
            password="testcancreate",
            object_channel="default"
        )

        client = APIClient()
        client.force_authenticate(user=user)

        data = copy.deepcopy(base_project)
        data["name"] = ""

        response = client.post(reverse("project-list"), data, format="json")
        self.assertTrue(
            response.data["name"][0] == "This field may not be blank."
        )

    def test_project_retrieval(self):
        """Assert projects can be retrieved"""
        user = User.objects.create_user(
            email="test_retrieval@gmail.com",
            password="testretrieval",
            object_channel="default"
        )

        client = APIClient()
        client.force_authenticate(user=user)

        data = copy.deepcopy(base_project)
        response = client.post(reverse("project-list"), data, format="json")

        response = client.get(
            reverse("project-detail", ["test-project"]),
            format="json"
        )

        self.assertTrue(response.data["name"] == data["name"])
        self.assertTrue(response.data["slug"] == "test-project")
        self.assertTrue(response.data["details"] == data["details"])
        self.assertTrue(response.data["description"] == data["description"])
        self.assertTrue(response.data["published"] is False)
        self.assertTrue(type(response.data["owner"]) in [dict, OrderedDict])
        self.assertTrue(isinstance(response.data["applies"], list))
        self.assertTrue(isinstance(response.data["applied_count"], int))
        self.assertTrue(
            isinstance(
                response.data["max_applies_from_roles"],
                int))
        self.assertTrue(len(response.data["causes"]) == 2)
        self.assertTrue(len(response.data["skills"]) == 2)

    def test_roles_with_id_fail(self):
        """Assert serializer doesn't accept roles with id"""
        user = User.objects.create_user(
            email="test_can_create_project@gmail.com",
            password="testcancreate",
            object_channel="default"
        )

        data = copy.deepcopy(base_project)
        data["roles"] = [{
            "name": "test",
            "prerequisites": "test2",
            "details": "test3",
            "vacancies": 5
        }]

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(reverse("project-list"), data, format="json")
        self.assertTrue(response.status_code == 201)

        data["roles"][0]["id"] = 25535
        response = client.post(reverse("project-list"), data, format="json")
        self.assertTrue(response.status_code == 201)
        self.assertNotEqual(
            Project.objects.get(pk=response.data["id"]).roles.first().pk,
            25535
        )


class ProjectCloseTestCase(TestCase):

    def setUp(self):
        ChannelSetting.objects.create(
            key="CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION",
            value="1",
            object_channel="default"
        )
        cache.clear()

        user = User.objects.create_user(
            email="test_close@gmail.com",
            password="testclose",
            object_channel="default"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=user)

        data = copy.deepcopy(base_project)
        self.project = self.client.post(
            reverse("project-list"),
            data,
            format="json"
        )

    def test_cant_close_project_if_not_owner_or_organization_member(self):
        """
        Assert that it's not possible to close a project if not the owner
        or organization member
        """
        user = User.objects.create_user(
            email="otheruser@gmail.com",
            password="otheruser",
            object_channel="default"
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse("project-close", ["test-project"]),
            format="json"
        )
        self.assertTrue(response.status_code == 403)

    def test_can_close_project(self):
        """ Assert that it's possible to close a project """
        response = self.client.post(
            reverse("project-close", ["test-project"]),
            format="json"
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(Project.objects.get(slug="test-project").closed)


class ProjectPostTestCase(TestCase):

    def setUp(self):
        user = User.objects.create_user(
            email="test_comment@gmail.com",
            password="testcomment",
            object_channel="default"
        )
        self.gallery = Gallery.objects.create(
            owner=user,
            object_channel="default"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=user)

        ChannelSetting.objects.create(
            key="CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION",
            value="1",
            object_channel="default"
        )
        cache.clear()

        data = copy.deepcopy(base_project)
        self.project = self.client.post(
            reverse("project-list"),
            data,
            format="json"
        )

    def test_only_owner_or_organization_member_can_post(self):
        post = {"content": "test"}
        self.client = APIClient()

        # Unauthenticated
        response = self.client.post(
            reverse("project-post", ["test-project"]),
            post,
            format="json"
        )
        self.assertEqual(response.status_code, 401)

        # Not part of organization
        testuser = User.objects.create_user(
            email="test_comment1@gmail.com",
            password="testcomment",
            object_channel="default"
        )
        self.client.force_authenticate(user=testuser)
        response = self.client.post(
            reverse("project-post", ["test-project"]),
            post,
            format="json"
        )
        self.assertEqual(response.status_code, 403)

        # As organization owner
        organization = Organization.objects.create(
            name="test",
            owner=testuser,
            object_channel="default"
        )
        Project.objects.filter(slug="test-project").update(
            organization=organization
        )
        response = self.client.post(
            reverse("project-post", ["test-project"]),
            post,
            format="json"
        )
        self.assertEqual(response.status_code, 200)

        # As organization member
        testuser2 = User.objects.create_user(
            email="test_comment2@gmail.com",
            password="testcomment",
            object_channel="default"
        )
        self.client.force_authenticate(user=testuser2)
        organization.members.add(testuser2)
        response = self.client.post(
            reverse("project-post", ["test-project"]),
            post,
            format="json"
        )
        self.assertEqual(response.status_code, 200)

    def test_user_can_post_in_project(self, content="test content"):
        """ Assert that user can post in project """
        post = {
            "title": "title",
            "content": content,
        }
        response = self.client.post(
            reverse("project-post", ["test-project"]),
            post,
            format="json"
        )
        self.assertTrue(response.status_code == 200)

    def test_post_with_gallery_and_documents(self):
        post = {
            "content": "test",
            "gallery": Gallery.objects.last().pk
        }
        response = self.client.post(
            reverse("project-post", ["test-project"]),
            post,
            format="json"
        )
        self.assertTrue(response.status_code == 200)
        self.assertEqual(response.data["gallery"], Gallery.objects.last().pk)

        response = self.client.get(
            reverse("project-detail", ["test-project"]),
            format="json"
        )
        self.assertEqual(
            response.data['posts'][0]['gallery']['id'],
            Gallery.objects.last().pk
        )

    def test_unpublished_posts(self, content="test content"):
        """
        Assert that unpublished posts come flagged
        """
        post = {
            "content": content,
        }
        response = self.client.post(
            reverse("project-post", ["test-project"]),
            post,
            format="json"
        )
        Post.objects.all().update(published=False)
        response = self.client.get(
            reverse("project-detail", ["test-project"]),
            format="json"
        )
        self.assertEqual(response.data['posts'][0]['published'], False)

    def test_retrieve_posts(self):
        self.test_user_can_post_in_project(content="a")
        self.test_user_can_post_in_project(content="b")
        self.test_user_can_post_in_project(content="c")
        response = self.client.get(
            reverse("project-detail", ["test-project"]),
            format="json"
        )

        self.assertEqual(len(response.data['posts']), 3)
        self.assertEqual(response.data['posts'][0]['content'], "c")
        self.assertEqual(response.data['posts'][1]['content'], "b")
        self.assertEqual(response.data['posts'][2]['content'], "a")

    def test_update_posts(self):
        data = {
            "title": "updated",
            "content": "updated",
            "gallery": Gallery.objects.last().pk,
        }
        self.test_user_can_post_in_project()
        post_pk = Post.objects.last().pk

        response = self.client.get(
            reverse("project-detail", ["test-project"]),
            format="json"
        )
        self.assertEqual(response.data['posts'][0]['content'], "test content")
        self.assertEqual(response.data['posts'][0]['title'], "title")
        self.assertEqual(response.data['posts'][0]['gallery'], None)

        response = self.client.patch(
            reverse(
                "project-post-patch-delete",
                [
                    "test-project",
                    Post.objects.last().pk + 1
                ]
            ),
            data,
            format="json"
        )
        self.assertEqual(response.status_code, 404)

        response = self.client.patch(
            reverse(
                "project-post-patch-delete",
                [
                    "test-project",
                    Post.objects.last().pk
                ]
            ),
            data,
            format="json"
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("project-detail", ["test-project"]),
            format="json"
        )
        self.assertEqual(response.data['posts'][0]['content'], "updated")
        self.assertEqual(
            response.data['posts'][0]['gallery']['id'],
            Gallery.objects.last().pk
        )

    def test_only_owner_or_organization_member_can_update_post(self):
        self.test_user_can_post_in_project()
        self.client = APIClient()
        post_pk = Post.objects.last().pk

        data = {
            "title": "updated",
            "content": "updated",
            "gallery": Gallery.objects.last().pk,
        }

        # Unauthenticated
        response = self.client.patch(
            reverse(
                "project-post-patch-delete",
                [
                    "test-project",
                    Post.objects.last().pk
                ]
            ),
            data,
            format="json"
        )
        self.assertEqual(response.status_code, 401)

        # Not part of organization
        testuser = User.objects.create_user(
            email="test_comment1@gmail.com",
            password="testcomment",
            object_channel="default"
        )
        self.client.force_authenticate(user=testuser)
        response = self.client.patch(
            reverse(
                "project-post-patch-delete",
                [
                    "test-project",
                    Post.objects.last().pk
                ]
            ),
            data,
            format="json"
        )
        self.assertEqual(response.status_code, 403)

        # As organization owner
        organization = Organization.objects.create(
            name="test",
            owner=testuser,
            object_channel="default"
        )
        Project.objects.filter(slug="test-project").update(
            organization=organization
        )
        response = self.client.patch(
            reverse(
                "project-post-patch-delete",
                [
                    "test-project",
                    Post.objects.last().pk
                ]
            ),
            data,
            format="json"
        )
        self.assertEqual(response.status_code, 200)

        # As organization member
        testuser2 = User.objects.create_user(
            email="test_comment2@gmail.com",
            password="testcomment",
            object_channel="default"
        )
        self.client.force_authenticate(user=testuser2)
        organization.members.add(testuser2)
        response = self.client.patch(
            reverse(
                "project-post-patch-delete",
                [
                    "test-project",
                    Post.objects.last().pk
                ]
            ),
            data,
            format="json"
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_post(self):
        self.test_user_can_post_in_project()
        self.client = APIClient()
        post_pk = Post.objects.last().pk

        # Unauthenticated
        response = self.client.delete(
            reverse(
                "project-post-patch-delete",
                [
                    "test-project",
                    Post.objects.last().pk
                ]
            ),
            format="json"
        )
        self.assertEqual(response.status_code, 401)

        # Not part of organization
        testuser = User.objects.create_user(
            email="test_comment1@gmail.com",
            password="testcomment",
            object_channel="default"
        )
        self.client.force_authenticate(user=testuser)
        response = self.client.delete(
            reverse(
                "project-post-patch-delete",
                ["test-project", Post.objects.last().pk]
            ),
            format="json"
        )
        self.assertEqual(response.status_code, 403)

        # As organization owner
        organization = Organization.objects.create(
            name="test",
            owner=testuser,
            object_channel="default"
        )
        Project.objects.filter(slug="test-project").update(
            organization=organization
        )
        response = self.client.delete(
            reverse(
                "project-post-patch-delete",
                ["test-project", Post.objects.last().pk]
            ),
            format="json"
        )
        self.assertEqual(response.status_code, 204)

        response = self.client.get(
            reverse(
                "project-detail",
                ["test-project"]
            ),
            format="json"
        )
        self.assertEqual(len(response.data['posts']), 0)


class ProjectWithOrganizationTestCase(TestCase):

    def setUp(self):
        cache.clear()

        self.user = User.objects.create_user(
            email="test_can_create_project@gmail.com",
            password="testcancreate",
            object_channel="default"
        )
        self.second_user = User.objects.create_user(
            email="test_second_user@test.com",
            password="testcancreate",
            object_channel="default"
        )
        self.third_user = User.objects.create_user(
            email="test_third_user@test.com",
            password="testcancreate",
            object_channel="default"
        )
        self.data = copy.deepcopy(base_project)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_no_organization(self):
        """Test no organization returns error"""
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(
            response.data["organization"] == ["This field is required."]
        )
        self.assertTrue(response.status_code == 400)

    def test_organization_is_int(self):
        """Test organization field must be int"""
        self.data['organization_id'] = 'str'

        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(
            response.data["organization_id"]
            == ["A valid integer is required."]
        )
        self.assertTrue(response.status_code == 400)

    def test_user_is_owner_or_member(self):
        """
        Test user is owner or member of organization
        """
        wrong_org = Organization(name="test", type=0, owner=self.second_user)
        wrong_org.save(object_channel="default")

        self.data['organization_id'] = wrong_org.pk
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(response.status_code == 403)

    def test_can_create_in_any_organization_if_settings_allow(self):
        """
        Test user can create project inside any
        organization if properly configured
        """
        ChannelSetting.objects.create(
            key="CAN_CREATE_PROJECTS_IN_ANY_ORGANIZATION",
            value="1",
            object_channel="default"
        )
        cache.clear()

        wrong_org = Organization(name="test", type=0, owner=self.second_user)
        wrong_org.save(object_channel="default")

        self.data['organization_id'] = wrong_org.pk
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(response.status_code == 201)

    def test_can_create(self):
        """Test user can create project with valid organization"""
        organization = Organization(name="test", type=0, owner=self.user)
        organization.save(object_channel="default")
        organization.members.add(self.second_user)

        self.data['organization_id'] = organization.pk
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(response.status_code == 201)

        self.client.force_authenticate(self.second_user)
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(response.status_code == 201)

    def test_can_hide_address(self):
        """Test user can create project with valid organization"""
        org = Organization(name="test", type=0, owner=self.user)
        org.save(object_channel="default")
        org.members.add(self.second_user)

        self.data['organization_id'] = org.pk
        self.data['hidden_address'] = True
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )

        # Owner retrieving
        response = self.client.get(
            reverse(
                "project-detail",
                ["test-project"]
            ),
            format="json"
        )
        self.assertTrue(
            response.data["address"]["typed_address"]
            == self.data["address"]["typed_address"]
        )
        self.assertTrue(response.data["hidden_address"] is True)

        # Organization member retrieving
        self.client.force_authenticate(self.second_user)
        response = self.client.get(
            reverse(
                "project-detail",
                ["test-project"]
            ),
            format="json"
        )
        self.assertTrue(
            response.data["address"]["typed_address"]
            == self.data["address"]["typed_address"]
        )
        self.assertTrue(response.data["hidden_address"] is True)

        # Non member retrieving
        self.client.force_authenticate(self.third_user)
        response = self.client.get(
            reverse(
                "project-detail",
                ["test-project"]
            ),
            format="json"
        )
        self.assertTrue(response.data["address"] is None)
        self.assertTrue(response.data["hidden_address"] is True)

        # Project without organization
        self.client.force_authenticate(self.second_user)
        Project.objects.filter(slug="test-project").update(
            organization=None
        )
        response = self.client.get(
            reverse(
                "project-detail",
                ["test-project"]
            ),
            format="json"
        )
        self.assertTrue(response.data["address"] is None)
        self.assertTrue(response.data["hidden_address"] is True)

    def test_can_create_project_with_another_owner(self):
        """
        Assert that it's possible to create a project with another owner
        """
        ChannelSetting.objects.create(
            key="CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION",
            value="1",
            object_channel="default"
        )
        cache.clear()

        client = APIClient()
        client.force_authenticate(user=self.user)

        data = copy.deepcopy(base_project)
        data["owner"] = self.second_user.pk

        # Without organization
        response = client.post(reverse("project-list"), data, format="json")
        self.assertTrue(response.status_code == 400)
        self.assertTrue(
            response.data["owner"][0]
            == "Organization field must be set to set owner."
        )

        # Not part of the organization
        organization = Organization(name="test", type=0, owner=self.user)
        organization.save(object_channel="default")
        data["organization_id"] = organization.pk
        response = client.post(reverse("project-list"), data, format="json")
        self.assertTrue(response.status_code == 400)
        self.assertTrue(
            response.data["owner"][0]
            == "User is a not a member of the organization."
        )

        # Part of the organization
        organization.members.add(self.second_user)
        response = client.post(reverse("project-list"), data, format="json")
        self.assertTrue(response.status_code == 201)
        project = Project.objects.get(pk=response.data["id"])
        self.assertTrue(project.owner.id == self.second_user.id)


class ProjectResourceUpdateTestCase(TestCase):

    def setUp(self):
        ChannelSetting.objects.create(
            key="CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION",
            value="1",
            object_channel="default"
        )
        cache.clear()

        self.user = User.objects.create_user(
            email="test_can_create_project@gmail.com",
            password="testcancreate",
            object_channel="default"
        )
        self.data = copy.deepcopy(base_project)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        Channel.objects.create(slug="test-channel")
        c = Cause.objects.create(
            name="other-channel",
            object_channel="test-channel"
        )
        s = Skill.objects.create(
            name="other-channel",
            object_channel="test-channel"
        )
        g = Gallery.objects.create(
            name="other-channel",
            owner=self.user,
            object_channel="test-channel"
        )
        ct = Category.objects.create(
            name="other-channel",
            object_channel="test-channel"
        )
        u = UploadedDocument.objects.create(
            name="other-channel",
            object_channel="test-channel"
        )
        self.data["causes"].append({"id": c.id})
        self.data["skills"].append({"id": s.id})
        self.data["galleries"] = [{"id": g.id}]
        self.data["documents"] = [{"id": u.id}]
        self.data["categories"] = [{"id": ct.id}]

        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(response.status_code == 201)

    def test_wrong_user_cant_update(self):
        """Test only owner can update project"""
        wrong_user = User.objects.create_user(
            email="wrong_user@gmail.com",
            password="testcancreate",
            object_channel="default"
        )
        wrong_user.save()
        self.client.force_authenticate(user=wrong_user)

        response = self.client.patch(
            reverse(
                "project-detail",
                ["test-project"]
            ),
            {},
            format="json"
        )
        self.assertTrue(response.status_code == 403)

    def test_update_fields_without_organization(self):
        """
        Test patch request update fields without organization field
        """
        ChannelSetting.objects.all().delete()
        cache.clear()

        updated_project = {
            "name": "test update",
            "details": "update",
            "description": "update",
            "causes": [{"id": 3}],
            "skills": [
                {"id": 1},
                {"id": 2},
                {"id": 3}
            ]
        }
        response = self.client.patch(
            reverse(
                "project-detail",
                ["test-project"]
            ),
            updated_project,
            format="json"
        )
        self.assertTrue(response.status_code == 200)

    def test_update_fields(self):
        """Test patch request update fields"""
        updated_project = {
            "name": "test update",
            "details": "update",
            "description": "update",
            "causes": [{"id": 3}],
            "skills": [
                {"id": 1},
                {"id": 2},
                {"id": 3}
            ],
            "galleries": [],
            "documents": [],
            "categories": []
        }
        response = self.client.patch(
            reverse(
                "project-detail",
                ["test-project"]
            ),
            updated_project,
            format="json"
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.data["name"] == "test update")
        self.assertTrue(response.data["details"] == "update")
        self.assertTrue(response.data["description"] == "update")

        # Don't erase associations with other channel objects
        self.assertTrue(len(response.data["causes"]) == 2)
        self.assertTrue(len(response.data["skills"]) == 4)
        self.assertTrue(
            result_contains(response.data["causes"], "name", "other-channel")
        )
        self.assertTrue(
            result_contains(response.data["skills"], "name", "other-channel")
        )
        self.assertTrue(len(response.data["galleries"]) == 1)
        self.assertTrue(len(response.data["documents"]) == 1)
        self.assertTrue(len(response.data["categories"]) == 1)

        user = User.objects.create_user(
            email="another@user.com",
            password="testcancreate",
            object_channel="default"
        )
        organization = Organization(name="test", type=0, owner=self.user)
        organization.save(object_channel="default")
        organization.members.add(user)
        project = Project.objects.get(pk=response.data['id'])
        project.organization = organization
        project.save()
        self.client.force_authenticate(user)
        response = self.client.patch(
            reverse(
                "project-detail",
                ["test-project"]
            ),
            updated_project,
            format="json"
        )
        self.assertTrue(response.status_code == 200)

    def test_update_address(self):
        """Test patch request update address resource"""
        updated_project = {
            "address": {
                "typed_address": "r. capote valente, 701, sao paulo"
            }
        }
        response = self.client.patch(
            reverse(
                "project-detail",
                ["test-project"]
            ),
            updated_project,
            format="json"
        )

        self.assertTrue(response.status_code == 200)
        self.assertTrue(
            response.data["address"]["typed_address"]
            == "r. capote valente, 701, sao paulo"
        )

    def test_update_disponibility(self):
        """Test patch request update disponibility resource"""
        updated_project = {
            "disponibility": {
                "type": "job",
                "job": {
                    "dates": [
                        {
                            "name": "update",
                            "start_date": "2013-01-29T12:34:56.123Z",
                            "end_date": "2013-01-29T13:34:56.123Z"
                        },
                        {
                            "name": "test1",
                            "start_date": "2013-02-01T12:34:56.123Z",
                            "end_date": "2013-02-01T13:34:56.123Z"
                        }
                    ]
                }
            }
        }
        response = self.client.patch(
            reverse(
                "project-detail",
                ["test-project"]
            ),
            updated_project,
            format="json"
        )

        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.data["disponibility"]["type"] == "job")
        self.assertTrue(
            response.data["disponibility"]["job"]["dates"][0]["name"]
            == "update"
        )

        updated_project = {
            "disponibility": {
                "type": "work",
                "work": {"description": "update"}
            }
        }
        response = self.client.patch(
            reverse(
                "project-detail",
                ["test-project"]
            ),
            updated_project,
            format="json"
        )

        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.data["disponibility"]["type"] == "work")
        self.assertTrue(
            response.data["disponibility"]["work"]["description"]
            == "update"
        )

    def test_update_roles(self):
        """Test patch request update roles resource"""
        updated_project = {
            "roles": [
                {
                    "name": "test",
                    "prerequisites": "test2",
                    "details": "test3",
                    "vacancies": 10
                }
            ]
        }
        response = self.client.patch(
            reverse(
                "project-detail",
                ["test-project"]
            ),
            updated_project,
            format="json"
        )

        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.data["max_applies_from_roles"], 10)
        self.assertTrue(
            response.data["roles"][0]["name"] == updated_project["roles"][0]["name"])
        self.assertTrue(response.data["roles"][0]["prerequisites"]
                        == updated_project["roles"][0]["prerequisites"])
        self.assertTrue(
            response.data["roles"][0]["details"] == updated_project["roles"][0]["details"])
        self.assertTrue(response.data["roles"][0]["vacancies"]
                        == updated_project["roles"][0]["vacancies"])
        self.assertTrue(response.data["roles"][0]["applied_count"] == 0)


class DisponibilityTestCase(TestCase):

    def setUp(self):
        ChannelSetting.objects.create(
            key="CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION",
            value="1",
            object_channel="default"
        )
        cache.clear()

        self.user = User.objects.create_user(
            email="test_can_create_project@gmail.com",
            password="testcancreate",
            object_channel="default"
        )
        self.data = copy.deepcopy(base_project)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_no_disponibility(self):
        """Test no disponibility returns error"""
        del self.data["disponibility"]
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(
            response.data["disponibility"]
            == ["This field is required."]
        )
        self.assertTrue(response.status_code == 400)

    def test_disponibility_type_required(self):
        """Test disponibility type is required"""
        self.data["disponibility"] = {}
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(
            response.data["disponibility"]["type"]
            == ["This field is required."]
        )
        self.assertTrue(response.status_code == 400)

    def test_type_not_work_or_job(self):
        """Test disponibility type can't be different than work or job"""
        self.data["disponibility"] = {"type": "test"}
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(
            response.data["disponibility"]["type"]
            == ["Must have either be 'work' or 'job'."]
        )
        self.assertTrue(response.status_code == 400)

    def test_empty_job_or_work(self):
        """Test empty job or work returns error"""
        self.data["disponibility"] = {"type": "job"}
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(
            response.data["disponibility"]["job"]
            == ["This field is required if type=\"job\"."]
        )
        self.assertTrue(response.status_code == 400)

        self.data["disponibility"] = {"type": "work"}
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(
            response.data["disponibility"]["work"]
            == ["This field is required if type=\"work\"."]
        )
        self.assertTrue(response.status_code == 400)

    def test_correct_work(self):
        """Test correct work returns success"""
        self.data["disponibility"] = {
            "type": "work",
            "work": {
                "description": "test desc",
                "weekly_hours": 6
            }
        }
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(response.data["disponibility"]["type"] == "work")
        self.assertTrue(
            response.data["disponibility"]["work"]["description"]
            == "test desc"
        )
        self.assertTrue(
            response.data["disponibility"]["work"]["weekly_hours"] == 6
        )
        self.assertTrue(response.status_code == 201)

    def test_job_dates_required(self):
        """Test job dates is required"""
        self.data["disponibility"] = {"type": "job", "job": {}}
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(
            response.data["disponibility"]["job"]["dates"]
            == ["This field is required."]
        )
        self.assertTrue(response.status_code == 400)

    def test_job_dates_cant_be_empty(self):
        """Test job dates can't be empty"""
        self.data["disponibility"] = {"type": "job", "job": {"dates": []}}
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(
            response.data["disponibility"]["job"]["dates"]
            == ["Must have at least one date."]
        )
        self.assertTrue(response.status_code == 400)

    def test_job_dates_cant_be_wrong_type(self):
        """Test job dates can't be wrong type"""
        self.data["disponibility"] = {"type": "job", "job": {"dates": ''}}
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(
            response.data["disponibility"]["job"]["dates"]["non_field_errors"]
            == ["Expected a list of items but got type \"str\"."]
        )
        self.assertTrue(response.status_code == 400)

    def test_job_dates_cant_have_bad_formatted_date(self):
        """Test job dates can't have bad formatted date"""
        self.data["disponibility"] = {
            "type": "job",
            "job": {
                "dates": [
                    {
                        "start_date": "abc",
                        "end_date": "abc"
                    }
                ]
            }
        }
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(
            response.data["disponibility"]["job"]["dates"][0]["start_date"]
            == [
                "Datetime has wrong format. Use one of these formats instead:"
                " YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."
            ]
        )
        self.assertTrue(
            response.data["disponibility"]["job"]["dates"][0]["end_date"]
            == [
                "Datetime has wrong format. Use one of these formats instead:"
                " YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."
            ]
        )
        self.assertTrue(response.status_code == 400)

    def test_job_returns_success(self):
        """Test correct job returns success"""
        def treat_date(date: str):
            return dateutil \
                    .parser \
                    .parse(date) \
                    .astimezone(pytz.utc) \
                    .isoformat() \
                    .replace('+00:00', 'Z')

        self.data["disponibility"] = {
            "type": "job",
            "job": {
                "dates": [
                    {
                        "name": "test1",
                        "start_date": "2013-01-29T12:34:56.123Z",
                        "end_date": "2013-01-29T13:34:56.123Z"
                    },
                    {
                        "name": "test1",
                        "start_date": "2013-02-01T12:34:56.123Z",
                        "end_date": "2013-02-01T13:34:56.123Z"
                    }
                ]
            }
        }
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(response.status_code == 201)
        self.assertTrue(
            treat_date(response.data["disponibility"]["job"]["dates"][0]["start_date"])
            == "2013-01-29T12:34:56.123000Z"
        )
        self.assertTrue(
            treat_date(response.data["disponibility"]["job"]["dates"][0]["end_date"])
            == "2013-01-29T13:34:56.123000Z"
        )
        self.assertTrue(
            treat_date(response.data["disponibility"]["job"]["dates"][1]["start_date"])
            == "2013-02-01T12:34:56.123000Z"
        )
        self.assertTrue(
            treat_date(response.data["disponibility"]["job"]["dates"][1]["end_date"])
            == "2013-02-01T13:34:56.123000Z"
        )

        self.assertTrue(
            treat_date(response.data["disponibility"]["job"]["start_date"])
            == "2013-01-29T12:34:56.123000Z"
        )
        self.assertTrue(
            treat_date(response.data["disponibility"]["job"]["end_date"])
            == "2013-02-01T13:34:56.123000Z"
        )


class VolunteerRoleTestCase(TestCase):
    def setUp(self):
        ChannelSetting.objects.create(
            key="CAN_CREATE_PROJECTS_WITHOUT_ORGANIZATION",
            value="1",
            object_channel="default"
        )
        cache.clear()

        self.user = User.objects.create_user(
            email="test_can_create_project@gmail.com",
            password="testcancreate",
            object_channel="default"
        )
        self.data = copy.deepcopy(base_project)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_roles_is_correct_type(self):
        """Test roles is correct type"""
        self.data["roles"] = {
            "name": "test",
            "prerequisites": "test2",
            "details": "test3",
            "vacancies": 5
        }
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(
            response.data["roles"]["non_field_errors"]
            == ["Expected a list of items but got type \"dict\"."]
        )
        self.assertTrue(response.status_code == 400)

    def test_roles_get_saved(self):
        """Test roles get saved"""
        self.data["roles"] = [
            {
                "name": "test",
                "prerequisites": "test2",
                "details": "test3",
                "vacancies": 5
            }
        ]
        response = self.client.post(
            reverse("project-list"),
            self.data,
            format="json"
        )
        self.assertTrue(response.status_code == 201)
        self.assertTrue(response.data["max_applies_from_roles"] == 5)
        self.assertTrue(response.data["roles"][0]["name"] == "test")
        self.assertTrue(response.data["roles"][0]["prerequisites"] == "test2")
        self.assertTrue(response.data["roles"][0]["details"] == "test3")
        self.assertTrue(response.data["roles"][0]["vacancies"] == 5)
        self.assertTrue("id" in response.data["roles"][0])

        response = self.client.get(
            reverse(
                "project-detail",
                ['test-project']
            ),
            format="json"
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.data["roles"][0]["name"] == "test")
        self.assertTrue(response.data["roles"][0]["prerequisites"] == "test2")
        self.assertTrue(response.data["roles"][0]["details"] == "test3")
        self.assertTrue(response.data["roles"][0]["vacancies"] == 5)
        self.assertTrue("id" in response.data["roles"][0])

    def test_cant_update_unowned_role(self):
        """Assert serializer doesn't accept roles with id"""
        data = copy.deepcopy(base_project)
        data["name"] = "project 1"
        data["roles"] = [{
            "name": "test",
            "prerequisites": "test",
            "details": "test",
            "vacancies": 5
        }]
        response = self.client.post(
            reverse("project-list"),
            data,
            format="json"
        )
        self.assertTrue(response.status_code == 201)
        vr1 = VolunteerRole.objects.filter(
            project__slug=response.data['slug']) .first()

        data = copy.deepcopy(base_project)
        data["name"] = "project 2"
        data["roles"] = [{
            "name": "another role",
            "prerequisites": "test2",
            "details": "test2",
            "vacancies": 5
        }]
        response = self.client.post(
            reverse("project-list"), data, format="json")
        self.assertTrue(response.status_code == 201)
        vr2 = VolunteerRole.objects.filter(
            project__slug=response.data['slug']) .first()

        data = {
            "roles": [
                {
                    "id": vr2.pk,
                    "name": "aaaaa",
                    "prerequisites": "aaaaa",
                    "details": "aaaa",
                    "vacancies": 5
                },
                {  # this should fail as vr1.pk is related to another project
                    "id": vr1.pk,
                    "name": "bbbbb",
                    "prerequisites": "bbbbb",
                    "details": "bbbb",
                    "vacancies": 5
                }
            ]
        }
        response = self.client.patch(
            reverse(
                "project-detail",
                [response.data["slug"]]
            ),
            data,
            format="json"
        )
        self.assertTrue(response.status_code == 200)
        self.assertEqual(response.data["roles"][0]["name"], "aaaaa")
        self.assertEqual(VolunteerRole.objects.get(pk=vr2.pk).name, "aaaaa")

        self.assertEqual(response.data["roles"][1]["name"], "bbbbb")
        self.assertNotEqual(response.data["roles"][1]["id"], "bbbbb")
        self.assertEqual(VolunteerRole.objects.get(pk=vr1.pk).name, "test")
