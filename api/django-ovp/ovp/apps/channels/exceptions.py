from rest_framework import status
from rest_framework.exceptions import APIException


class UnexpectedChannelAssociationError(Exception):
    def __init__(self):
        msg = "You can't associate a channel directly to single \
               channel models. Pass object_channel to .save() \
               or objects.create() method instead."
        super().__init__(msg)


class NoChannelSupplied(Exception):
    def __init__(self):
        msg = "A channel was expected but no channel was supplied."
        super().__init__(msg)


class InterceptRequest(Exception):
    def __init__(self, response):
        self.response = response
