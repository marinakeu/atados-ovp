from os import getenv

from haystack.query import SQ
from django.db.models import Q
from ovp.apps.core.models import Cause
from ovp.apps.core.models import Skill
from ovp.apps.projects.models import Category
from ovp.apps.projects.models import Project
from ovp.apps.projects.models import Apply
from ovp.apps.organizations.models import Organization

from ovp.apps.channels.content_flow import BaseContentFlow
from ovp.apps.channels.content_flow import NoContentFlow
from ovp.apps.channels.content_flow import CFM

class BaseChannelContentFlow(BaseContentFlow):
  source = "default"
  destination = "base"

  def get_filter_searchqueryset_q_obj(self, model_class):
    if model_class in [Project, Organization]:
      return SQ()

    raise NoContentFlow

  def get_filter_queryset_q_obj(self, model_class):
    if model_class in [Cause, Skill, Project, Organization, Apply]:
      return Q()

    raise NoContentFlow

if getenv('ENABLE_BASE_CONTENT_FLOW'):
  CFM.add_flow(BaseChannelContentFlow())
