from ovp.apps.projects import models
from ovp.apps.channels.serializers import ChannelRelationshipSerializer
from rest_framework import serializers


##############
#  Validators
##############

def dates_validator(data):
    dates = data.get('dates', None)

    if len(dates) < 1:
        raise serializers.ValidationError(
            {"dates": ["Must have at least one date."]}
        )

    for date in dates:
        sr = JobDateSerializer(data=date)
        sr.is_valid(raise_exception=True)

##############
#  Serializers
##############


class JobDateSerializer(ChannelRelationshipSerializer):

    class Meta:
        model = models.JobDate
        fields = ['name', 'start_date', 'end_date']


class JobSerializer(ChannelRelationshipSerializer):

    dates = JobDateSerializer(many=True)

    class Meta:
        model = models.Job
        fields = [
            'can_be_done_remotely',
            'dates',
            'project',
            'start_date',
            'end_date'
        ]
        read_only_fields = ['start_date', 'end_date']
        extra_kwargs = {'project': {'write_only': True}}
        validators = [dates_validator]

    def create(self, validated_data):
        dates = validated_data.pop('dates')

        job = super(JobSerializer, self).create(validated_data)

        for date in dates:
            sr = JobDateSerializer(data=date, context=self.context)
            date_obj = sr.create(date)
            job.dates.add(date_obj)
        job.update_dates()

        return job
