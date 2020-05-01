from django.apps import AppConfig

class ShellConfig(AppConfig):
  name = 'channels.shell'

  def ready(self):
    from . import content_flow
