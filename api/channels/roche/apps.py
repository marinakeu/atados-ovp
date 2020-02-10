from django.apps import AppConfig

class RocheConfig(AppConfig):
  name = 'channels.roche'

  def ready(self):
    from . import content_flow
