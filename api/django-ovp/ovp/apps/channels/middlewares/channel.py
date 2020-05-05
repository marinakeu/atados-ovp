import re
from ovp.apps.channels.cache import get_channel

from rest_framework.request import Request

from django.http import JsonResponse
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import redirect
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.middleware import get_user
from django.conf import settings

import urllib.parse as parse

from rest_framework_jwt.authentication import JSONWebTokenAuthentication


def get_user_jwt_or_oauth2(request):
    user = get_user(request)

    if user.is_authenticated:
        return user

    # JWT
    try:
        from rest_framework_jwt.authentication import (
            JSONWebTokenAuthentication
        )

        try:
            user_jwt = JSONWebTokenAuthentication()
            user_jwt = user_jwt.authenticate(Request(request))
            if user_jwt is not None:
                return user_jwt[0]
        except Exception:
            pass
    except ModuleNotFoundError:
        pass

    # OAuth2
    try:
        from oauth2_provider.contrib.rest_framework import OAuth2Authentication

        try:
            user_o2 = OAuth2Authentication().authenticate(request)
            if user_o2 is not None:
                return user_o2[0]
        except Exception:
            pass
    except ModuleNotFoundError:
        pass

    return user


class ChannelRecognizerMiddleware(object):
    """
    This middleware is responsible for identifying and
    making request.channel available.

    It must precede corsheaders middleware because corsheaders
    use this information to determine the allowed domains from
    the channel settings.

    Although the API can be used for multiple channels
    on a single domain through headers, it is not possible
    to do so for the admin page. Therefore, you must
    always point a domain like "{channel-name}.admin.tld" to your server.
    This is how this middleware identify if it is a admin
    request or an api request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request = self._add_channel(request)

        response = self.get_response(request)

        # Add channel header to response
        response["X-OVP-Channel"] = request.channel
        return response

    def _add_channel(self, request):
        request = self._add_admin_request_info(request)

        if request.is_admin_page:
            request.channel = request.admin_channel_domain
        else:
            request.channel = request.META.get(
                "HTTP_X_OVP_CHANNEL",
                "default"
            ).strip()
        return request

    def _add_admin_request_info(self, request):
        absolute_url = request.build_absolute_uri(request.get_full_path())
        parsed_url = parse.urlparse(absolute_url)
        domains = parsed_url.netloc.split(".")

        if len(domains) >= 3 and "admin" == domains[1]:
            request.is_admin_page = True
            request.admin_channel_domain = domains[0]
        else:
            request.is_admin_page = False
            request.admin_channel_domain = None

        return request


class ChannelProcessorMiddleware():
    """
    This middleware is responsible for several things.

    In case of API:
    - Check it is a valid channel request
    - If the request tries to hit /admin/ or /jet/, return 404
    - Check the provided user token corresponds to the request channel

    In case of Admin:
    - Check it is a valid channel request
    - Redirect to /admin/ if not hitting an admin route.
        (Trying to access the api through a channel admin subdomain)
    - Check user is on the same channel as the request

    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.is_admin_page:
            return self.admin_processor(request)
        else:
            return self.api_processor(request)

    def admin_processor(self, request):
        # Check for invalid channel
        if get_channel(request.channel) is None:
            return HttpResponse("Invalid channel.", status=400)

        # Check if user is acessing an admin
        # subdomain and not going to an admin route
        # Redirect if necessary
        if self._admin_should_redirect_to_admin_page(request):
            return redirect("/admin")

        # Check user
        if not self._check_admin_permissions(request):
            return HttpResponse("Invalid channel for user.", status=400)

        return self.get_response(request)

    def api_processor(self, request):
        # Check for invalid channel
        if get_channel(request.channel) is None:
            return JsonResponse({"detail": "Invalid channel."}, status=400)

        # Redirect 404 if trying to access admin
        # without going through a channel subdomain
        self._404_admin(request)

        # Check user
        if not self._check_api_permissions(request):
            resp = {"detail": "Invalid channel for user token."}
            return JsonResponse(resp, status=400)

        return self.get_response(request)

    def _check_api_permissions(self, request):
        # https://github.com/GetBlimp/django-rest-framework-jwt/issues/45
        user = get_user_jwt_or_oauth2(request)
        if user.is_authenticated:
            user_channel = user.channel.slug
            if request.channel != user_channel:
                return False
        return True

    def _check_admin_permissions(self, request):
        # Allow the request to go through
        # if authenticated user is on the correct channel
        if request.user.is_authenticated \
           and request.user.channel.slug == request.channel:
            return True

        # Allow the request to go through if user is unauthenticated
        if not request.user.is_authenticated:
            return True

        return False

    @property
    def _enabled_languages_regex(self):
        return "|".join(
            ["{}/".format(x[0]) for x in settings.LANGUAGES]
        )

    def _404_admin(self, request):
        path = request.get_full_path()
        if re.match(r'^/({})?admin'.format(self._enabled_languages_regex), path) \
            or path.startswith("/admin") \
            or path.startswith("/jet"):
            raise Http404
        return False

    def _admin_should_redirect_to_admin_page(self, request):
        path = request.get_full_path()

        if not re.match(r'^/({})?admin'.format(self._enabled_languages_regex), path) \
           and not path.startswith("/jet") \
           and not path.startswith("/static") \
           and not path.startswith("/martor"):
            return True

        return False
