from haystack.query import SQ
from django.db.models import Q
from ovp.apps.projects.models import Category
from ovp.apps.projects.models import Project
from ovp.apps.projects.models import Apply
from ovp.apps.organizations.models import Organization

from ovp.apps.channels.content_flow import BaseContentFlow
from ovp.apps.channels.content_flow import NoContentFlow
from ovp.apps.channels.content_flow import CFM

class ICNContentFlow(BaseContentFlow):
  source = "default"
  destination = "icn"

  def __init__(self):
    try:
      self.category_id = Category.objects.get(slug="instituto-center-norte").pk
    except:
      self.category_id = None

  def get_filter_searchqueryset_q_obj(self, model_class):
    if model_class == Project:
      return SQ(organization_categories=self.category_id)

    elif model_class == Organization:
      return SQ(categories=self.category_id)

    raise NoContentFlow

  def get_filter_queryset_q_obj(self, model_class):
    if model_class == Project:
      return Q(organization__categories=self.organizations_id)
    elif model_class == Organization:
      return Q(categories=self.organizations_id)
    elif model_class == Apply:
      return Q(project__organization__categories=self.organizations_id)

    raise NoContentFlow

CFM.add_flow(ICNContentFlow())
