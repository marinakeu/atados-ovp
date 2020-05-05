from ovp.apps.core.helpers.bookmark import annotate_bookmark

from ovp.apps.projects.models import Project
from ovp.apps.organizations.models import Organization
from ovp.apps.users.models.user import User


def get_organization_queryset(request=None):
    queryset = Organization.objects.filter(deleted=False) \
        .prefetch_related('causes') \
        .select_related('address', 'channel') \
        .order_by('-highlighted')
    queryset = annotate_bookmark(queryset, request=request)
    return queryset


def get_project_queryset(request=None):
    queryset = Project.objects \
        .prefetch_related('skills', 'causes', 'categories', 'job__dates') \
        .select_related('address', 'owner', 'work', 'job', 'channel') \
        .filter(deleted=False) \
        .order_by('-pk')
    queryset = annotate_bookmark(queryset, request=request)
    return queryset
