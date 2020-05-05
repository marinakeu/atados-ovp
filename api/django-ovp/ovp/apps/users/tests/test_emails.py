from django.test import TestCase
from django.core import mail

from ovp.apps.users.models import (
    User, PasswordRecoveryToken, EmailVerificationToken
)


class TestEmailTriggers(TestCase):
    def test_user_creation_trigger_email(self):
        """Assert that email is triggered when creating an user"""
        user = User(email="a@b.c", password="validpassword", name="valid name")
        user.save(object_channel="default")
        # Welcome and email verification
        self.assertTrue(len(mail.outbox) == 2)

    def test_email_verification_token_creation_trigger_email(self):
        """
        Assert that email is triggered when email
        verification token is created
        """
        user = User(email="d@e.f", password="validpassword", name="valid name")
        user.save(object_channel="default")

        mail.outbox = []
        token = EmailVerificationToken(user=user)
        token.save(object_channel="default")
        self.assertTrue(len(mail.outbox) == 1)

    def test_token_creation_trigger_email(self):
        """
        Assert that email is triggered when password recovery token is created
        """
        user = User(email="d@e.f", password="validpassword", name="valid name")
        user.save(object_channel="default")

        mail.outbox = []
        token = PasswordRecoveryToken(user=user)
        token.save(object_channel="default")
        self.assertTrue(len(mail.outbox) == 1)

    def test_async_email_works(self):
        """Assert that async emails are triggered by testing user creation"""
        user = User(email="a@b.c", password="validpassword", name="valid name")
        user.save(object_channel="default")
        mail.outbox = []
        user.mailing(async_mail=True).sendWelcome().join()
        self.assertTrue(len(mail.outbox) > 0)
