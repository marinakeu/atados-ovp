from django.core.mail import EmailMultiAlternatives, get_connection
from django.template import Template
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist
from django.conf import settings
from django.utils import translation
from ovp.apps.core.helpers import is_email_enabled, get_email_subject
from ovp.apps.channels.cache import get_channel_setting
import os
import json

import threading
import sys


class EmailThread(threading.Thread):
    def __init__(self, msg):
        self.msg = msg
        threading.Thread.__init__(self)

    def run(self):
        return self.msg.send() > 0


class BaseMail:
    """
    This class is responsible for firing emails
    """
    from_email = ''

    def __init__(self, email_address, channel=None,
                 async_mail=None, locale=None):
        self.channel = channel
        self.email_address = email_address
        self.async_mail = async_mail
        self.locale = locale or getattr(settings, "LANGUAGE_CODE", "en-us")
        self.all_emails = json.loads(
            os.environ.get("EMAIL_FROM_POSSIBILITIES", "{}")
        )
        self.all_users = json.loads(
            os.environ.get("EMAIL_USER_POSSIBILITIES", "{}")
        )
        self.all_passwords = json.loads(
            os.environ.get("PASSWORD_POSSIBILITIES", "{}")
        )

    def sendEmail(self, template_name, subject, context={}):
        if not is_email_enabled(self.channel, template_name):
            return False

        # Inject extra context
        ctx = inject_client_url(self.channel, context)
        ctx["extend"] = {
            "html": "{}/email/base-body.html".format(self.channel),
            "txt": "{}/email/base-body.txt".format(self.channel)
        }

        self.__setLocale()
        subject = get_email_subject(self.channel, template_name, subject)
        text_content, html_content = self.__render(template_name, ctx)
        self.__resetLocale()

        from_email = self.all_emails.get(self.channel, self.from_email)
        from_user = self.all_users.get(self.channel, settings.EMAIL_HOST_USER)
        from_password = self.all_passwords.get(
            self.channel,
            settings.EMAIL_HOST_PASSWORD
        )
        connection = get_connection(
            username=from_user,
            password=from_password,
        )
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            [self.email_address],
            connection=connection
        )
        msg.attach_alternative(html_content, "text/html")

        async_flag = None
        if self.async_mail:
            async_flag = "async"
        elif self.async_mail is None:
            async_flag = getattr(settings, "DEFAULT_SEND_EMAIL", "async")

        if async_flag == "async":
            t = EmailThread(msg)
            t.start()
            result = t
        else:
            result = msg.send() > 0

        return result

    def __render(self, template_name, ctx):
        test_channels = getattr(settings, "TEST_CHANNELS", [])

        try:
            text_content = get_template(
                '{}/email/{}-body.txt'.format(self.channel, template_name)
            ).render(ctx)
            html_content = get_template(
                '{}/email/{}-body.html'.format(self.channel, template_name)
            ).render(ctx)
        except TemplateDoesNotExist as e:
            # This avoids template errors when testing with non-default channel
            if self.channel in test_channels:
                return ("", "")

            # Re-raise if not a test channel
            raise(e)

        return (text_content, html_content)

    def __setLocale(self):
        self.__active_locale = translation.get_language()
        translation.activate(self.locale)

    def __resetLocale(self):
        translation.activate(self.__active_locale)
        self.__active_locale = None

    def render(self, template_name, ctx):
        return self.__render(template_name, ctx)


class ContactFormMail(BaseMail):
    """
    This class is reponsible for firing emails sent through the contact form
    """

    def __init__(self, recipients, channel=None, async_mail=None, locale=None):
        self.channel = channel
        self.recipients = recipients
        self.async_obj = async_mail
        self.locale = locale

    def sendContact(self, context={}):
        """
        Send contact form message to single or multiple recipients
        """
        for recipient in self.recipients:
            super().__init__(
                recipient,
                channel=self.channel,
                async_mail=self.async_obj,
                locale=self.locale
            )
            self.sendEmail('contactForm', 'New contact form message', context)


#
# Helpers
#

def inject_client_url(channel, ctx):
    ctx['CLIENT_URL'] = get_channel_setting(channel, "CLIENT_URL")[0]
    return ctx
