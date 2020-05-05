from rest_framework.serializers import Serializer
from rest_framework.serializers import RelatedField
from rest_framework.serializers import SerializerMethodField
from rest_framework.serializers import ChoiceField
from rest_framework.serializers import ValidationError
from rest_framework.serializers import CharField
from rest_framework.serializers import FloatField

from ovp.apps.channels.serializers import ChannelRelationshipSerializer

from ovp.apps.ratings.models import Rating
from ovp.apps.ratings.models import RatingRequest
from ovp.apps.ratings.models import RatingParameter
from ovp.apps.ratings.models import RatingAnswer
from ovp.apps.ratings.models import POSSIBLE_TYPES
from ovp.apps.users.models import User
from ovp.apps.projects.models import Project
from ovp.apps.organizations.models import Organization


def get_object_type(obj):
    if isinstance(obj, User):
        return 'user'
    elif isinstance(obj, Project):
        return 'project'
    elif isinstance(obj, Organization):
        return 'organization'
    raise Exception('Unexpected type of tagged object')


class RatedObject(RelatedField):
    def to_representation(self, obj):
        from ovp.apps.projects.serializers.project import (
            ProjectRetrieveSerializer
        )
        from ovp.apps.organizations.serializers import (
            OrganizationRetrieveSerializer
        )
        from ovp.apps.users.serializers import (
            ShortUserPublicRetrieveSerializer
        )

        obj_type = get_object_type(obj)
        if obj_type == 'user':
            return ShortUserPublicRetrieveSerializer(
                obj, context=self.context).data
        elif obj_type == 'project':
            return ProjectRetrieveSerializer(obj, context=self.context).data
        elif obj_type == 'organization':
            return OrganizationRetrieveSerializer(
                obj, context=self.context).data


class RatingParameterRetriveSetrializer(ChannelRelationshipSerializer):
    type = SerializerMethodField()

    class Meta:
        model = RatingParameter
        fields = ['slug', 'description', 'type']

    def get_type(self, obj):
        return obj.get_type_display()


class RatingRequestRetrieveSerializer(ChannelRelationshipSerializer):
    rated_object = RatedObject(read_only=True)
    object_type = SerializerMethodField(read_only=True)
    rating_parameters = RatingParameterRetriveSetrializer(
        many=True, read_only=True)

    class Meta:
        model = RatingRequest
        fields = [
            'uuid',
            'created_date',
            'rated_object',
            'object_type',
            'rating_parameters']

    def get_object_type(self, obj):
        return get_object_type(obj.rated_object)


class RatingAnswerCreateSerializer(Serializer):
    parameter_slug = CharField()
    value_quantitative = FloatField(required=False)
    value_qualitative = CharField(required=False)

    class Meta:
        fields = [
            'rating',
            'parameter_slug',
            'value_qualitative',
            'value_quantitative']

    def create(self, data, *args, **kwargs):
        # Parameter
        data['parameter'] = RatingParameter.objects.get(
            slug=data.pop('parameter_slug', None))

        # Rating
        data['rating'] = self.context['rating']

        return RatingAnswer.objects.create(
            object_channel=self.context['request'].channel, **data)

    def validate(self, data, *args, **kwargs):
        try:
            parameter = RatingParameter.objects.get(
                slug=data['parameter_slug'])
        except RatingParameter.DoesNotExist:
            return super(
                RatingAnswerCreateSerializer,
                self).validate(
                data,
                *args,
                **kwargs)

        if parameter.type == 2:
            value = data.get('value_quantitative', None)

            if value is not None:
                if value < 0 or value > 1:
                    raise ValidationError(
                        '\'value_quantitative\' must be between 0 and 1 '
                        'for qualitative parameters.'
                    )

        if parameter.type == 3:
            value = data.get('value_quantitative', None)

            if value is not None:
                if value != 0 and value != 1:
                    raise ValidationError(
                        '\'value_quantitative\' must be 0 or 1 '
                        'for boolean parameters.'
                    )
        return super().validate(data, *args, **kwargs)


class RatingCreateSerializer(ChannelRelationshipSerializer):
    answers = RatingAnswerCreateSerializer(many=True)

    class Meta:
        model = Rating
        fields = ['owner', 'answers', 'request']

    def create(self, data, *args, **kwargs):
        answers = data.pop('answers', [])
        rating = super(
            RatingCreateSerializer,
            self).create(
            data,
            *
            args,
            **kwargs)

        self.context['rating'] = rating
        for answer in answers:
            serializer = RatingAnswerCreateSerializer(
                data=answer, context=self.context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return rating

    def validate(self, data, *args, **kwargs):
        rating_request = self.context["rating_request"]
        tmp_rating_request_parameter_slugs = [
            x.slug for x in rating_request.rating_parameters.all()]

        try:
            if Rating.objects.get(request=rating_request):
                raise ValidationError("This request has already been rated.")
        except Rating.DoesNotExist:
            pass

        self.validate_duplicated_parameters(data)
        self.validate_missing_parameters(
            data, tmp_rating_request_parameter_slugs)
        self.validate_extra_parameters(
            data, tmp_rating_request_parameter_slugs)

        return super(
            RatingCreateSerializer,
            self).validate(
            data,
            *
            args,
            **kwargs)

    def validate_duplicated_parameters(self, data):
        slugs = [answer["parameter_slug"] for answer in data["answers"]]

        if len(slugs) != len(set(slugs)):
            raise ValidationError(
                "You have sent multiple answers for a parameter."
                " Check you request body."
            )

    def validate_missing_parameters(self, data, request_parameter_slugs):
        sent_slugs = [answer["parameter_slug"] for answer in data["answers"]]
        missing = []

        for parameter in request_parameter_slugs:
            if parameter not in sent_slugs:
                missing.append(parameter)

        if len(missing):
            raise ValidationError(
                "The following parameters are missing: {}.".format(
                    ", ".join(missing)))

    def validate_extra_parameters(self, data, request_parameter_slugs):
        for answer in data["answers"]:
            if answer["parameter_slug"] not in request_parameter_slugs:
                raise ValidationError(
                    "Invalid parameter '{}' for request.".format(
                        answer["parameter_slug"]))
