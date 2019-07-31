from django.apps import AppConfig

class ICNConfig(AppConfig):
  name = 'channels.icn'

  def ready(self):
    from . import content_flow
