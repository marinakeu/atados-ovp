from haystack.query import SQ
from django.db.models import Q
from ovp.apps.projects.models import Category
from ovp.apps.projects.models import Project
from ovp.apps.projects.models import Apply
from ovp.apps.core.models import Cause
from ovp.apps.core.models import Skill
from ovp.apps.organizations.models import Organization

from ovp.apps.channels.content_flow import BaseContentFlow
from ovp.apps.channels.content_flow import NoContentFlow
from ovp.apps.channels.content_flow import CFM

class RocheContentFlow(BaseContentFlow):
  source = "default"
  destination = "roche"

  def get_filter_searchqueryset_q_obj(self, model_class):
    if model_class == Project:
      return SQ()
    elif model_class == Organization:
      return SQ()
    elif model_class in [Cause, Skill]:
      return SQ()

    raise NoContentFlow

  def get_filter_queryset_q_obj(self, model_class):
    if model_class == Project:
      return Q()
    elif model_class == Organization:
      return Q()
    elif model_class == Apply:
      return Q()
    elif model_class in [Cause, Skill]:
      return Q()

    raise NoContentFlow

CFM.add_flow(RocheContentFlow())
