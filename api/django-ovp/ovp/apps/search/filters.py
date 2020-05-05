from ovp.apps.search import helpers
from haystack.query import SQ

from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import NotAuthenticated

from django.db.models import When, F, IntegerField, Count, Case

from ovp.apps.core.models import Cause, Skill
from ovp.apps.users.models.profile import UserProfile
from ovp.apps.channels.cache import get_channel_setting
from ovp.apps.channels.content_flow import CFM

import json

from datetime import datetime

#####################
#  ViewSet filters  #
#####################


class UserSkillsCausesFilter:
    def get_skills_and_causes(
            self,
            user,
            no_check=False,
            append_assumed=False):
        if not no_check and not user.is_authenticated:
            raise NotAuthenticated()

        output = {"skills": [], "causes": []}

        try:
            if user.users_userprofile_profile:
                skills = user.users_userprofile_profile.skills
                causes = user.users_userprofile_profile.causes
                output["skills"] = skills.values_list('id', flat=True)
                output["causes"] = causes.values_list('id', flat=True)
        except UserProfile.DoesNotExist:
            pass

        if append_assumed:
            output["skills"] += Skill.objects.filter(
                project__apply__user=user).values_list(
                'pk', flat=True)
            output["causes"] += Causes.objects.filter(
                project__apply__user=user).values_list(
                'pk', flat=True)

        return output

    def annotate_queryset(
            self,
            queryset,
            user,
            no_check=False,
            append_assumed=False):
        skills_causes = self.get_skills_and_causes(user, no_check=no_check)

        queryset = queryset\
            .annotate(
                cause_relevance=Count(
                    Case(When(causes__pk__in=skills_causes["causes"], then=1),
                         output_field=IntegerField()),
                    distinct=True),
                skill_relevance=Count(
                    Case(When(skills__pk__in=skills_causes["skills"], then=1),
                         output_field=IntegerField()),
                    distinct=True))\
            .annotate(relevance=F('cause_relevance') + F('skill_relevance'))

        return queryset


class ProjectRelevanceOrderingFilter(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            if "relevance" in ordering or "-relevance" in ordering:
                queryset = UserSkillsCausesFilter().annotate_queryset(
                    queryset,
                    request.user
                )

        if ordering:
            return queryset.order_by(*ordering)

        return queryset


######################
#  Haystack filters  #
######################

def get_operator_and_items(string=''):
    items = string.split(',')

    if items[0] == "AND" or items[0] == "OR":
        first = items.pop(0)

        if first == "AND":
            return SQ.AND, items
        if first == "OR":
            return SQ.OR, items

    return SQ.OR, items


def by_channels(queryset, channel_string=None):
    """ Filter queryset by a comma delimeted channels list """
    queryset = queryset.filter(channel__in=channel_list)

    return queryset


def by_channel_content_flow(queryset, channel_string=None):
    queryset = CFM.filter_searchqueryset(channel_string, queryset)

    return queryset


def by_organizations(queryset, organization=None):
    """ Filter queryset by a comma delimeted organizations list """
    if organization:
        queryset = queryset.filter(organization__in=organization)

    return queryset


def by_skills(queryset, skill_string=None):
    """ Filter queryset by a comma delimeted skill list """
    if skill_string:
        operator, items = get_operator_and_items(skill_string)
        q_obj = SQ()
        for s in items:
            if len(s) > 0:
                q_obj.add(SQ(skills=s), operator)
        queryset = queryset.filter(q_obj)
    return queryset


def by_disponibility(queryset, disponibility_string=None):
    """ Filter queryset by a comma delimeted disponibility list """
    if disponibility_string:
        operator, items = get_operator_and_items(disponibility_string)
        q_obj = SQ()
        for d in items:
            if len(d) > 0 and d == 'job':
                q_obj.add(SQ(job=True), operator)
            elif len(d) > 0 and d == 'work':
                q_obj.add(SQ(work=True), operator)
            elif len(d) > 0 and d == 'remotely':
                q_obj.add(SQ(can_be_done_remotely=True), operator)

        queryset = queryset.filter(q_obj)
    return queryset


def by_date(queryset, date_string=None):
    """ Filter queryset by a comma delimeted date """
    if date_string:
        operator, items = get_operator_and_items(date_string)
        q_obj = SQ()
        date = datetime.strptime(items[0], '%Y-%m-%d').strftime('%Y-%m-%d')
        q_obj.add(SQ(start_date=date) | SQ(end_date=date), operator)

        queryset = queryset.filter(start_date=date)

    return queryset


def by_categories(queryset, category_string=None):
    """ Filter queryset by a comma delimeted category list """
    if category_string:
        operator, items = get_operator_and_items(category_string)
        q_obj = SQ()
        for c in items:
            if len(c) > 0:
                q_obj.add(SQ(categories=c), operator)
        queryset = queryset.filter(q_obj)
    return queryset


def by_causes(queryset, cause_string=None):
    """ Filter queryset by a comma delimeted cause list """
    if cause_string:
        operator, items = get_operator_and_items(cause_string)
        q_obj = SQ()
        for c in items:
            if len(c) > 0:
                q_obj.add(SQ(causes=c), operator)
        queryset = queryset.filter(q_obj)
    return queryset


def by_published(queryset, published_string='true'):
    """ Filter queryset by publish status """
    if published_string == 'true':
        queryset = queryset.filter(published=1)
    elif published_string == 'false':
        queryset = queryset.filter(published=0)
    # Any other value will return both published and unpublished
    return queryset


def by_closed(queryset, closed_string='true'):
    """ Filter queryset by closed status """
    if closed_string == 'true':
        queryset = queryset.filter(closed=1)
    elif closed_string == 'false':
        queryset = queryset.filter(closed=0)
    # Any other value will return both closed and open
    return queryset


def by_name(queryset, name=None):
    """ Filter queryset by name, with word wide auto-completion """
    if name:
        queryset = queryset.filter(name=name)
    return queryset


def by_address(queryset, address='', project=False):
    """
    Filter queryset by address

    If project=True, we also apply a project exclusive filter
    """
    if address:
        address = json.loads(address)

        if u'address_components' in address:
            q_objs = []

            if len(address['address_components']):
                for component in address['address_components']:
                    q_obj = SQ()
                    names = component['long_name']
                    names = names if type(names) is list else [names]
                    strs = [u"{}-{}".format(x, y) for x in names for y in component['types']]

                    for component_type in strs:
                        type_string = helpers.whoosh_raw(component_type)
                        q_obj.add(SQ(address_components=type_string), SQ.OR)
                        q_obj.add(SQ(skip_address_filter=1), SQ.OR)

                    q_objs.append(q_obj)

                # Filter all address components
                for obj in q_objs:
                    queryset = queryset.filter(obj)
            else:  # remote projects
                if project:
                    queryset = queryset.filter(can_be_done_remotely=1)
    return queryset


def filter_out(queryset, setting_name, channel):
    """
    Remove unwanted results from queryset
    """
    excluded_list = get_channel_setting(channel, setting_name)
    for excluded in excluded_list:
        key, value = excluded.split(":")
        key = key.strip().strip("\"").strip("''")
        value = value.strip().strip("\"").strip("''")
        queryset = queryset.exclude(**{key: value})

    return queryset
