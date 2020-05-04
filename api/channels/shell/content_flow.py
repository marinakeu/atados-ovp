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

class ShellContentFlow(BaseContentFlow):
  source = "default"
  destination = "shell"

  def __init__(self):
    try:
      self.category_id = Category.objects.get(slug="atados-to-shell").pk
    except:
      self.category_id = None

  def get_filter_searchqueryset_q_obj(self, model_class):
    if model_class == Project:
      return SQ(categories=self.category_id)

    elif model_class == Organization:
      return SQ(projects_categories=self.category_id)

    raise NoContentFlow

  def get_filter_queryset_q_obj(self, model_class):
    if model_class in [Cause, Skill]:
      return Q()
    elif model_class == Project:
      return Q(categories=self.category_id)
    elif model_class == Organization:
      return Q(project__categories=self.category_id)
    elif model_class == Apply:
      return Q(project__categories=self.category_id)

    raise NoContentFlow

CFM.add_flow(ShellContentFlow())
