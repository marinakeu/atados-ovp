from haystack.query import SQ
from django.db.models import Q
from ovp.apps.projects.models import Category
from ovp.apps.projects.models import Project
from ovp.apps.projects.models import Apply
from ovp.apps.organizations.models import Organization

from ovp.apps.channels.content_flow import BaseContentFlow
from ovp.apps.channels.content_flow import NoContentFlow
from ovp.apps.channels.content_flow import CFM

class RRPContentFlow(BaseContentFlow):
  source = "rrp"
  destination = "default"

  def __init__(self):
    self.organizations_id = [45, 1780, 2120]

  def get_filter_searchqueryset_q_obj(self, model_class):
    if model_class == Project:
      return SQ(organization__in=self.organizations_id)
    elif model_class == Organization:
      return SQ(org_id__in=self.organizations_id)

    raise NoContentFlow

  def get_filter_queryset_q_obj(self, model_class):
    if model_class == Project:
      return Q(organization__in=self.organizations_id)
    elif model_class == Organization:
      return Q(pk__in=self.organizations_id)
    elif model_class == Apply:
      return Q(project__organization_id__in=self.organizations_id)

    raise NoContentFlow

CFM.add_flow(RRPContentFlow())
