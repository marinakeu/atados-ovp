from django.apps import AppConfig

class GDDConfig(AppConfig):
  name = 'channels.gdd'

  def ready(self):
    from . import content_flow
    from . import signals
