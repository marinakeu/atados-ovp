from multiprocessing.dummy import Pool as ThreadPool
from bs4 import BeautifulSoup
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from ovp.apps.projects.models import Project
from ovp.apps.projects.models import Category
from ovp.apps.digest.emails import DigestEmail
from ovp.apps.digest.models import DigestLog
from ovp.apps.digest.models import DigestLogContent
from ovp.apps.digest.models import PROJECT
from ovp.apps.digest.backends.smtp import SMTPBackend
from ovp.apps.users.models import User
from ovp.apps.search.filters import UserSkillsCausesFilter
from ovp.apps.uploads import helpers
from django.db import connections
from django.db.models import Value, IntegerField, Q

import math
import time
import requests

config = {
    'interval': {
        #'minimum': 60 * 60 * 24 * 5,
        'minimum': 60 * 60 * 24 * 0,
        'maximum': 0
    },
    'projects': {
        'minimum': 1,
        'maximum': 6,
        'max_age': 60 * 60 * 24 * 7 * 2,
    }
}

class ContentGenerator():
    def __init__(self, threaded=True):
        self.threaded = threaded

    def generate_content_sync(self, users):
        content = []
        for user in users:
            content.append(self.generate_content_for_user(user))
        return filter(lambda x: x is not None, content)

    def generate_content_threaded(self, users):
        pool = ThreadPool(8)
        result = pool.map_async(
            self.generate_content_for_user,
            users,
            chunksize=4)
        real_result = result.get()
        pool.close()
        pool.join()
        return filter(lambda x: x is not None, real_result)

    def generate_content(self, email_list, campaign, channel='default'):
        print("generating content")
        content_dict = {}

        users = User.objects.prefetch_related(
            'users_userprofile_profile__causes',
            'users_userprofile_profile__skills'
        )
        users = users.select_related('channel')
        users = users.filter(channel__slug=channel, email__in=email_list)
        users = users.annotate(campaign=Value(campaign, IntegerField()))
        users = list(users)

        if self.threaded:
            content = self.generate_content_threaded(users)
        else:
            content = self.generate_content_sync(users)

        return content

    def generate_content_for_user(self, user):
        not_projects = list(
            DigestLogContent.objects.filter(
                digest_log__recipient=user.email,
                content_type=PROJECT,
                channel=user.channel
            ).values_list(
                'content_id',
                flat=True
            )
        )
        projects = Project.objects.filter(
            channel__slug=user.channel.slug,
            deleted=False,
            closed=False,
            published=True,
            published_date__gte=timezone.now() - relativedelta(
                seconds=config['projects']['max_age']
            ),
        )
        projects = projects.exclude(pk__in=not_projects)
        projects = projects.select_related('image', 'job', 'work', 'organization')
        projects = self.filter_by_address(projects, user)
        projects = UserSkillsCausesFilter().annotate_queryset(
            projects, user, no_check=True, append_assumed=True
        ).order_by("-relevance")
        projects = projects[:config["projects"]["maximum"]]

        if len(projects) < config["projects"]["minimum"]:
            return None

        return {
            "email": user.email,
            "channel": user.channel.slug,
            "campaign": user.campaign,
            "projects": [
                {
                    "pk": p.pk,
                    "name": p.name,
                    "slug": p.slug,
                    "description": p.description,
                    "organization_name": p.organization.name if p.organization else "",
                    "organization_slug": p.organization.slug if p.organization else "",
                    "image": (
                        p.image.image_small if (p.image
                                                and p.image.image_small) else ""
                    ),
                    "image_absolute": p.image.absolute if p.image else False,
                    "disponibility": p.job if hasattr(
                        p,
                        'job') else (
                        p.work if hasattr(
                            p,
                            'work') else None),
                    "disponibility_type": 'job' if hasattr(
                        p,
                        'job') else (
                        'work' if hasattr(
                            p,
                            'work') else None)} for p in projects
            ],
            "posts": []
            #"posts": self.get_blog_posts()
        }

    def filter_by_address(self, qs, user):
        if not user.profile or not user.profile.address:
            return qs
        state = user.profile.address.address_components.filter(
            types__name="administrative_area_level_1"
        ).first()

        if not state:
            return qs

        state = state.short_name
        area_level = "administrative_area_level_1"
        address_filter = Q(
            address__address_components__short_name=state,
            address__address_components__types__name=area_level,
            categories__id=21
        )
        remote_filter = Q(
            Q(work__can_be_done_remotely=True) | Q(job__can_be_done_remotely=True)
        )
        filtered_qs = qs.filter(
            address_filter | remote_filter
        )

        return filtered_qs if filtered_qs.count() > 0 else qs

    def get_blog_posts(self):
        try:
            response = requests.get(
                "https://blog.atados.com.br/wp-json/wp/v2/posts?per_page=2"
            )
        except requests.exceptions.ConnectionError:
            return { "posts": [] }
        return {
            "posts": [
                {
                    "url": x["link"],
                    "title": BeautifulSoup(
                        x["title"]["rendered"],
                        features="html.parser"
                    ).get_text(),
                    "excerpt": BeautifulSoup(
                        x["excerpt"]["rendered"],
                        features="html.parser"
                    ).get_text(),
                    "image": (
                        x["better_featured_image"]
                         ["media_details"]
                         ["sizes"]
                         ["medium"]
                         ["source_url"]
                    )
                } for x in response.json()
            ]
        }


class DigestCampaign():
    def __init__(self, channel="default", backend=SMTPBackend, campaign=None, backend_kwargs={}):
        self.channel = channel
        self.backend = backend(channel=channel, **backend_kwargs)
        self.cg = ContentGenerator()
        self._set_campaign(campaign)

    def _set_campaign(self, campaign=None):
        if campaign is not None:
            self.campaign = campaign
            return

        try:
            self.campaign = DigestLog.objects.order_by("-pk")[0].campaign + 1
        except IndexError:
            self.campaign = 1

    def _get_email_list(self):
        return set(
            User.objects
                .select_related('channel', 'users_userprofile_profile')
                .filter(
                    is_active=True,
                    channel__slug=self.channel,
                    is_subscribed_to_newsletter=True)
                .values_list('email', flat=True)
        )

    def _pre_filter(self, email_list):
        sent_recently = set(
            DigestLog.objects .filter(
                trigger_date__gt=timezone.now() -
                relativedelta(
                    seconds=config['interval']['minimum'])) .values_list(
                'recipient',
                flat=True))
        return set(filter(lambda x: x not in sent_recently, email_list))

    def send_campaign(self, chunk_size=0, channel="default", email_list=None):
        if not email_list:
            email_list = self._get_email_list(channel)

        user_list = list(self._pre_filter(email_list))

        if not len(user_list):
            print("0 users to send.")
            return

        try:
            chunks = math.ceil(len(user_list) / chunk_size)
        except ZeroDivisionError:
            chunks = 1
            chunk_size = len(user_list)

        if not len(user_list):
            return

        print(
            "Sending campaign {}.\nChunk size: {}\nChunks: {}".format(
                self.campaign,
                chunk_size,
                chunks))

        out = []
        # template_context = self.cg.get_blog_posts()
        template_context = {}
        for i in range(0, len(user_list), chunk_size):
            chunk_i = math.ceil(i / chunk_size) + 1

            print("Processing chunk {}/{}".format(chunk_i, chunks))
            chunk = user_list[i:i + chunk_size]
            content = self.cg.generate_content(chunk, self.campaign)

            out.append(self.backend.send_chunk(content, template_context))
        return out
