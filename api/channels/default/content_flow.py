from os import getenv
from ovp.apps.channels.content_flow import BaseContentFlow
from ovp.apps.channels.content_flow import CFM

class BaseContentFlow(BaseContentFlow):
  source = "default"
  destination = "base"


if getenv('ENABLE_BASE_CONTENT_FLOW'):
  CFM.add_flow(BaseContentFlow())
