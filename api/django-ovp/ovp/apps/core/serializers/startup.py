from ovp.apps.channels.content_flow import CFM
from rest_framework.serializers import Serializer
from rest_framework.fields import IntegerField
from ovp.apps.core.models import Skill
from ovp.apps.core.models import Cause
from ovp.apps.users.models import User
from ovp.apps.organizations.models import Organization
from .skill import SkillSerializer
from .cause import FullCauseSerializer


class StartupData(object):

    def __init__(self, request):
        self.skills = CFM.filter_queryset(
            request.channel,
            Skill.objects.all(),
            distinct=True
        )
        self.causes = CFM.filter_queryset(
            request.channel,
            Cause.objects.all(),
            distinct=True
        )
        self.volunteer_count = User.objects.filter(
            is_active=True,
            channel__slug=request.channel
        ).count()
        self.nonprofit_count = CFM.filter_queryset(
            request.channel,
            Organization.objects.filter(published=True),
            distinct=True
        ).count()


class StartupSerializer(Serializer):
    skills = SkillSerializer(many=True, required=False)
    causes = FullCauseSerializer(many=True, required=False)
    volunteer_count = IntegerField(required=False)
    nonprofit_count = IntegerField(required=False)
