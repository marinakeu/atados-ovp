from dateutil.relativedelta import relativedelta

from django.test import TestCase
from django.core.cache import cache

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from ovp.apps.users import models
from ovp.apps.users.tests.helpers import authenticate
from ovp.apps.users.tests.helpers import create_user

from ovp.apps.projects.models import Project
from ovp.apps.projects.models import Apply

from ovp.apps.channels.models.channel_setting import ChannelSetting


class UserResourceViewSetTestCase(TestCase):
    def setUp(self, *args, **kwargs):
        cache.clear()

    def test_can_create_user(self):
        """Assert that it's possible to create an user"""
        response = create_user()
        self.assertTrue(response.data['uuid'])
        self.assertTrue("password" not in response.data)

    def test_cant_create_user_duplicated_email(self):
        """
        Assert that it's not possible to create an user with a repeated email
        """
        response = create_user()
        self.assertTrue(response.data['uuid'])
        response = create_user()
        self.assertTrue(response.json(), {'email': ['An user with this email is already registered.']})

    def test_cant_create_user_duplicated_email_different_cases(self):
        """
        Assert that it's not possible to create an user with a repeated email
        even with different cases
        """
        response = create_user(email="validemail@email.com")
        self.assertTrue(response.data['uuid'])
        response = create_user(email="VALIDEMAIL@EMAIL.com")
        self.assertEqual(response.json(), {'email': ['An user with this email is already registered.']})

    def test_cant_create_user_invalid_password(self):
        """
        Assert that it's not possible to create an user with a repeated email
        """
        response = create_user(
            'test_cant_create_invalid_password@test.com', 'abc')
        self.assertTrue(len(response.data['password']) > 0)
        self.assertTrue(isinstance(response.data['password'], list))

    def test_can_create_user_with_valid_passwords(self):
        """
        Assert that it's possible to create an user
        with a series of valid passwords
        """
        passwords = [
            'thisisapassword',
            'password with spaces',
            '  thisisapassword  ']
        for i, password in enumerate(passwords):
            response = create_user(
                'testvalidpassword{}@test.com'.format(i), password)
            self.assertTrue(response.data['uuid'])
            self.assertTrue("password" not in response.data)

    def test_doesnt_return_password_on_user_creation(self):
        """Assert that the serializer does not return user hashed password """
        response = create_user()
        self.assertTrue(response.data.get('password', None) is None)

    def test_cant_patch_password_without_current_password(self):
        """
        Assert that it's not possible to update user
        password without the current password
        """
        response = create_user('test_can_patch_password@test.com', 'abcabcabc')
        u = models.User.objects.get(uuid=response.data['uuid'])

        data = {'password': 'pwpw12341234'}
        client = APIClient()
        client.force_authenticate(user=u)
        response = client.patch(
            reverse('user-current-user'),
            data,
            format="json"
        )
        self.assertTrue(response.status_code == 400)
        self.assertTrue(
            response.data["current_password"]
            == ["Invalid password."]
        )

    def test_can_patch_password(self):
        """Assert that it's possible to update user password"""
        response = create_user('test_can_patch_password@test.com', 'abcabcabc')
        u = models.User.objects.get(uuid=response.data['uuid'])

        data = {'password': 'pwpw12341234', 'current_password': 'abcabcabc'}
        client = APIClient()
        client.force_authenticate(user=u)
        response = client.patch(
            reverse('user-current-user'),
            data,
            format="json")
        self.assertTrue(response.status_code == 200)
        self.assertTrue("password" not in response.data)

        response = authenticate(
            'test_can_patch_password@test.com',
            data['password'])
        self.assertTrue(response.data['access_token'] is not None)

    def test_cant_update_invalid_password(self):
        """
        Assert that it's impossible to update user
        password to a invalid password
        """
        response = create_user('test_can_put_password@test.com', 'abcabcabc')
        u = models.User.objects.get(uuid=response.data['uuid'])

        data = {
            'name': 'abc',
            'password': 'abc',
            'current_password': 'abcabcabc'}
        client = APIClient()
        client.force_authenticate(user=u)
        response = client.patch(
            reverse('user-current-user'),
            data,
            format="json")
        self.assertTrue(response.status_code == 400)
        self.assertTrue(len(response.data['password']) > 0)
        self.assertTrue(isinstance(response.data['password'], list))

    def test_can_get_current_user(self):
        """Assert that authenticated users can get associated info"""
        user = create_user(
            'test_can_get_current_user@test.com',
            'validpassword')

        client = APIClient()
        client.login(
            username='test_can_get_current_user@test.com',
            password='validpassword',
            channel='default')
        response = client.get(reverse('user-current-user'), {}, format="json")
        self.assertTrue(response.data.get('email', None))
        self.assertTrue(response.data.get('name', None))
        self.assertTrue("expired_password" not in response.data)

    def test_expired_password_fields(self):
        """Assert that password expired field works"""
        ChannelSetting.objects.create(
            key="EXPIRE_PASSWORD_IN", value="{}".format(
                60 * 60), object_channel="default")
        cache.clear()

        user = create_user(
            'test_can_get_current_user@test.com',
            'validpassword')

        client = APIClient()
        client.login(
            username='test_can_get_current_user@test.com',
            password='validpassword',
            channel='default')

        response = client.get(reverse('user-current-user'), {}, format="json")
        self.assertTrue(response.data['expired_password'] is False)

        entry = models.PasswordHistory.objects.last()
        entry.created_date = entry.created_date - relativedelta(hours=1)
        entry.save()

        response = client.get(reverse('user-current-user'), {}, format="json")
        self.assertTrue(response.data['expired_password'])

    def test_can_create_hidden_user(self):
        """Assert that it's possible to create a hidden user"""
        response = create_user(extra_data={'public': False})
        self.assertTrue(response.data['public'] is False)

    def test_can_set_user_to_hidden(self):
        """Assert that it's possible to set public user to hidden user"""
        response = create_user()
        self.assertTrue(response.data['public'])

        user = models.User.objects.get(uuid=response.data['uuid'])
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.patch(
            reverse('user-current-user'), {'public': False}, format="json")
        self.assertTrue(response.data['public'] is False)

    def test_can_retrieve_public_user(self):
        """ Assert it's possible to retrieve a public profile """
        response = create_user()

        client = APIClient()
        response = client.get(
            reverse('public-users-detail', [response.data['slug']]),
            format="json"
        )
        self.assertTrue(response.data['slug'])
        self.assertTrue("applies" in response.data)

    def test_public_bookmarks(self):
        """ Assert user bookmarks are public """
        response = create_user()

        client = APIClient()
        response = client.get(
            reverse('public-users-detail', [response.data['slug']]),
            format="json"
        )
        self.assertTrue(isinstance(response.data["bookmarked_projects"], list))

    def test_hidden_bookmarks(self):
        """
        Assert user bookmarks are are hidden bookmarks if setting applied
        """
        ChannelSetting.objects.create(
            key="ENABLE_PUBLIC_USER_BOOKMARKED_PROJECTS",
            value="0",
            object_channel="default"
        )
        response = create_user()

        client = APIClient()
        response = client.get(
            reverse('public-users-detail', [response.data['slug']]),
            format="json"
        )
        self.assertTrue(response.data["bookmarked_projects"] is None)

    def test_cant_retrieve_hidden_user(self):
        """ Assert it's not possible to retrieve a hidden profile """
        slug = create_user(extra_data={'public': False}).data['slug']

        client = APIClient()
        response = client.get(
            reverse(
                'public-users-detail',
                [slug]),
            format="json")
        self.assertTrue(response.status_code == 404)

        create_user(email="a@b.com")
        client.force_authenticate(
            user=models.User.objects.get(
                email="a@b.com"))
        response = client.get(
            reverse(
                'public-users-detail',
                [slug]),
            format="json")
        self.assertTrue(response.status_code == 404)

    def test_can_retrieve_hidden_user_if_self(self):
        """ Assert it's possible to retrieve your own hidden profile """
        response = create_user(extra_data={'public': False})

        client = APIClient()
        client.force_authenticate(
            user=models.User.objects.get(
                email="validemail@gmail.com"))
        response = client.get(
            reverse('public-users-detail', [response.data['slug']]),
            format="json"
        )
        self.assertTrue(response.status_code == 200)

    def test_ask_for_credentials(self):
        """Assert that unauthenticated users can't get current user info"""
        client = APIClient()
        response = client.get(reverse('user-current-user'), {}, format="json")
        self.assertTrue(
            response.data['detail']
            == 'Authentication credentials were not provided.'
        )

    def test_can_deactivate_account(self):
        """
        Assert that it's possible to deactivate user account
        """
        response = create_user('test_can_patch_password@test.com', 'abcabcabc')
        u = models.User.objects.get(uuid=response.data['uuid'])
        p = Project.objects.create(name='test', owner=u, object_channel='default')
        Apply.objects.create(project=p, user=u, object_channel='default')

        self.assertEqual(Apply.objects.first().status, 'applied')
        data = {'password': 'pwpw12341234'}
        client = APIClient()
        client.force_authenticate(user=u)
        response = client.post(
            reverse('user-deactivate-account'),
            format="json"
        )
        u = models.User.objects.get(pk=u.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Apply.objects.first().status, 'unapplied-by-deactivation')
        self.assertEqual(u.is_active, False)


class UserPasswordHistoryTestCase(TestCase):
    def setUp(self):
        cache.clear()

    def test_can_update_to_same_or_old_password(self):
        """ Assert that it's possible to update to the same or old password """
        response = create_user(
            'test_can_patch_password@test.com',
            'old_password')
        user = models.User.objects.get(uuid=response.data['uuid'])

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(reverse('user-current-user'),
                                {'password': 'new_password',
                                 'current_password': 'old_password'},
                                format="json")
        self.assertTrue(response.status_code == 200)

        response = client.patch(reverse('user-current-user'),
                                {'password': 'new_password',
                                 'current_password': 'new_password'},
                                format="json")
        self.assertTrue(response.status_code == 200)

        response = client.patch(reverse('user-current-user'),
                                {'password': 'old_password',
                                 'current_password': 'new_password'},
                                format="json")
        self.assertTrue(response.status_code == 200)

    def test_cant_update_to_same_or_old_password_if_in_settings(self):
        """
        Assert that it's not possible to update to the same
        or old password if configured
        """
        ChannelSetting.objects.create(
            key="CANT_REUSE_LAST_PASSWORDS",
            value="2",
            object_channel="default"
        )
        cache.clear()

        response = create_user(
            'test_can_patch_password@test.com',
            'old_password')
        user = models.User.objects.get(uuid=response.data['uuid'])

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(reverse('user-current-user'),
                                {'password': 'new_password',
                                 'current_password': 'old_password'},
                                format="json")
        self.assertTrue(response.status_code == 200)

        response = client.patch(reverse('user-current-user'),
                                {'password': 'new_password',
                                 'current_password': 'new_password'},
                                format="json")
        self.assertTrue(response.status_code == 400)

        response = client.patch(reverse('user-current-user'),
                                {'password': 'old_password',
                                 'current_password': 'new_password'},
                                format="json")
        self.assertTrue(response.status_code == 400)

        response = client.patch(reverse('user-current-user'),
                                {'password': 'newest_password',
                                 'current_password': 'new_password'},
                                format="json")
        self.assertTrue(response.status_code == 200)

        response = client.patch(reverse('user-current-user'),
                                {'password': 'old_password',
                                 'current_password': 'newest_password'},
                                format="json")
        self.assertTrue(response.status_code == 200)
