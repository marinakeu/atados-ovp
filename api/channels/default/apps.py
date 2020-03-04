from django.apps import AppConfig

class DefaultConfig(AppConfig):
  name = 'channels.default'

  def ready(self):
    from . import signals
    from . import content_flow
