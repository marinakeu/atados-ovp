from django.test import TestCase
from django.core import mail

from ovp.apps.channels.models.channel_setting import ChannelSetting

import ovp.apps.core.emails
from django.core.cache import cache


class TestBaseMail(TestCase):

    def test_email_trigger(self):
        """
        Assert that email is sent to outbox
        """
        bm = ovp.apps.core.emails.BaseMail('a@b.c', channel="default")
        bm.sendEmail('base', '', {})
        self.assertTrue(len(mail.outbox) > 0)

    def test_async_email_trigger(self):
        """
        Assert that async emails are sent to outbox
        """
        bm = ovp.apps.core.emails.BaseMail(
            'a@b.c',
            channel="default",
            async_mail=True
        )
        bm.sendEmail('base', '', {}).join()
        self.assertTrue(len(mail.outbox) > 0)

    def test_email_subject_can_be_overridden(self):
        """
        Assert that email subject can be overridden
        """
        bm = ovp.apps.core.emails.BaseMail('a@b.c', channel="default")
        bm.sendEmail('base', 'test', {})
        subject = "Override email subjects by creating " \
                  "a template named {emailTemplate}-subject.txt"
        self.assertTrue(mail.outbox[0].subject == subject)


class TestDisableMail(TestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_email_can_be_disabled(self):
        """
        Assert that email can be disabled
        """
        ChannelSetting.objects.create(
            key="DISABLE_EMAIL",
            value="base",
            object_channel="default"
        )

        bm = ovp.apps.core.emails.BaseMail('a@b.c', channel="default")
        bm.sendEmail('base', '', {})
        self.assertTrue(len(mail.outbox) == 0)
