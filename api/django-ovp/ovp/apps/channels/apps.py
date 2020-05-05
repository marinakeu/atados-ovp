from django.apps import AppConfig


class ChannelsConfig(AppConfig):
    name = 'ovp.apps.channels'

    def ready(self):
        from . import signals
        from . import content_flow
