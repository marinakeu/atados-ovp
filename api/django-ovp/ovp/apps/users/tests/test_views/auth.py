from django.test import TestCase

from ovp.apps.users.models import User

from ovp.apps.channels.models import Channel

from ovp.apps.users.tests.helpers import authenticate
from ovp.apps.users.tests.helpers import create_user
from ovp.apps.users.tests.helpers import create_token

from rest_framework.reverse import reverse
from rest_framework.test import APIClient


class OAuth2AuthTestCase(TestCase):
    def test_can_login(self):
        """ Assert that it's possible to login """
        user = create_user('test_can_login@test.com', 'validpassword')
        response = authenticate()
        self.assertTrue(response.data['access_token'] is not None)

    def test_cant_login_deactivated(self):
        """ Assert that it's not possible to login with deactivated account """
        create_user('test_can_login@test.com', 'validpassword')
        u = User.objects.filter(email='test_can_login@test.com').update(is_active=False)
        response = authenticate()
        self.assertEqual(response.status_code, 401)
        expected_response = {
            'error': {
                'detail': 'This user is deactivated and can not login anymore.',
                'name': 'UserDeactivated'
            },
            'success': False
        }
        self.assertEqual(response.data, expected_response)

    def test_cant_login_wrong_password(self):
        """ Assert that it's not possible to login with wrong password """
        user = create_user('test_can_login@test.com', 'invalidpassword')
        response = authenticate()
        self.assertTrue(
            response.data == {
                "error": "invalid_grant",
                "error_description": "Invalid credentials given."})

    def test_can_login_two_users_same_email(self):
        """
        Assert that it's possible to login if two users have
        the same email on different channels.
        """
        Channel.objects.create(name="Test", slug="test-channel")
        user1 = User.objects.create(
            email="test_can_login@test.com",
            password="validpassword",
            object_channel="default")
        user2 = User.objects.create(
            email="test_can_login@test.com",
            password="validpassword",
            object_channel="test-channel")

        response = authenticate()
        token = response.data['access_token']
        response = APIClient().get(
            reverse('user-current-user'),
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token))
        self.assertEqual(response.data["uuid"], str(user1.uuid))

        response = authenticate(headers={"HTTP_X_OVP_CHANNEL": "test-channel"})
        token = response.data['access_token']
        response = APIClient().get(
            reverse('user-current-user'),
            format="json",
            HTTP_AUTHORIZATION="Bearer {}".format(token),
            HTTP_X_OVP_CHANNEL="test-channel")
        self.assertEqual(response.data["uuid"], str(user2.uuid))

    def test_can_login_with_wrong_email_case(self):
        """
        Assert it's possible to login even if the email case is wrong
        """
        user1 = User.objects.create(
            email="test_can_login@test.com",
            password="validpassword",
            object_channel="default")

        response = authenticate(email="TEST_CAN_LOGIN@TEST.com", password="validpassword")
        self.assertTrue(response.data['access_token'] is not None)

    def test_cant_register_same_email_with_different_cases(self):
        """
        Assert it's not possible to register the same email with different cases
        """
        pass
