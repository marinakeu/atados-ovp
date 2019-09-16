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

class GDDContentFlow(BaseContentFlow):
  source = "default"
  destination = "gdd"

  def __init__(self):
    try:
      self.category_id = Category.objects.get(slug="export-to-gdd-2020").pk
    except:
      self.category_id = None

  def get_filter_searchqueryset_q_obj(self, model_class):
    if model_class == Project:
      #return SQ(organization_categories=self.category_id)
      return SQ()

    elif model_class == Organization:
      #return SQ(categories=self.category_id)
      return SQ()

    raise NoContentFlow

  def get_filter_queryset_q_obj(self, model_class):
    if model_class == Project:
      #return Q(organization__categories=self.category_id)
      return Q()
    elif model_class == Organization:
      #return Q(categories=self.category_id)
      return Q()
    elif model_class == Apply:
      #return Q(project__organization__categories=self.category_id)
      return Q()

    raise NoContentFlow

CFM.add_flow(GDDContentFlow())
