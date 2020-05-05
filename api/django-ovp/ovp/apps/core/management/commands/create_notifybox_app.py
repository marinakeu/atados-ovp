import logging
from django.core.management.base import BaseCommand
from ovp.apps.core.notifybox import NotifyBoxApi
from ovp.apps.channels.models import ChannelSetting

def set_aws_credentials(channel, aws_credentials):
    api_key = ChannelSetting.objects.get(channel__slug = channel, key="NOTIFYBOX_ACCESS_KEY").value
    api_secret = ChannelSetting.objects.get(channel__slug = channel, key="NOTIFYBOX_SECRET_KEY").value

    api = NotifyBoxApi(access_key=api_key, secret_key=api_secret)
    api.setAwsCredentials(*aws_credentials)

def create_app(channel, admin_secret):
    # Create app
    api = NotifyBoxApi(admin_secret=admin_secret)
    result = api.createApp(f'Channel: {channel}')
    access_key = result['createApp']['access_key']
    secret = result['createApp']['secret']

    # Clear settings
    (ChannelSetting.objects
        .filter(
            channel__slug = channel,
            key__in=["NOTIFYBOX_ACCESS_KEY", "NOTIFYBOX_SECRET_KEY", "NOTIFYBOX_TOKEN"])
        .delete())

    # Create settings
    ChannelSetting.objects.create(object_channel = channel, key="NOTIFYBOX_ACCESS_KEY", value=access_key)
    ChannelSetting.objects.create(object_channel = channel, key="NOTIFYBOX_SECRET_KEY", value=secret)

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'channel',
            help='Channel slug',
            type=str,
        )

        parser.add_argument(
            'notifications-admin-secret',
            help='Notification admin secret',
            type=str,
        )

        parser.add_argument(
            '--set-aws-credentials',
            help='Set aws credentials',
            nargs=3
        )

    def handle(self, *args, **options):
        # Converts value from verbosity int to logging library
        # level.
        # 1 -> 30 (logging.WARNING)
        # 2 -> 20 (logging.INFO)
        # 3 -> 10 (logging.DEBUG)
        loggingLevel = 40 - (options['verbosity'] * 10)

        logger = logging.getLogger()
        console = logging.StreamHandler()

        logger.setLevel(loggingLevel)
        console.setLevel(loggingLevel)

        logger.addHandler(console)

        create_app(options['channel'], options['notifications-admin-secret'])

        if options['set_aws_credentials']:
            set_aws_credentials(options['channel'], options['set_aws_credentials'])
