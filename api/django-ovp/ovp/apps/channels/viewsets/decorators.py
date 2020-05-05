from ovp.apps.channels.signals import before_channel_request
from ovp.apps.channels.signals import after_channel_request
from ovp.apps.channels.exceptions import InterceptRequest
from ovp.apps.channels.content_flow import CFM


def ChannelViewSet(cls):
    """
    Wrapping any viewset with this decorator will make get_queryset result
    get filtered by channel set on the request header.
    It also adds signals to dispatch view which channels can attach
    to override the view behavior.

    Use for viewsets that handle a Channel resource.
    """
    # Patch get queryset
    get_queryset = getattr(cls, "get_queryset", None)
    if get_queryset:
        def patched_get_queryset(self, *args, **kwargs):
            return CFM.filter_queryset(
                self.request.channel,
                get_queryset(self, *args, **kwargs),
                distinct=True
            )
        cls.get_queryset = patched_get_queryset

    # We also patch the queryset
    queryset = getattr(cls, "queryset", None)
    if queryset is not None:
        @property
        def patched_queryset(self):
            return CFM.filter_queryset(self.request.channel, queryset)
        cls.queryset = patched_queryset

    # If get_queryset calls self.queryset, there's no problem filtering twice
    # as django evaluates queries lazily

    def patched_dispatch(self, request, *args, **kwargs):  # View signals
        """
        This is the same as rest_framework dispatch method, only with
        signals added before and after the view
        """
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers

        try:
            self.initial(request, *args, **kwargs)

            # Get the appropriate handler method
            if request.method.lower() in self.http_method_names:
                handler = getattr(
                    self, request.method.lower(),
                    self.http_method_not_allowed
                )
            else:
                handler = self.http_method_not_allowed

            # Dispatch a signal and allow handler to block the request
            try:
                before_channel_request.send(sender=cls, request=request)
            except InterceptRequest as e:
                return self.finalize_response(request, e.response)

            response = handler(request, *args, **kwargs)

            # Dispatch a signal and allow handler to override the response
            try:
                after_channel_request.send(
                    sender=cls,
                    request=request,
                    response=response
                )
            except InterceptRequest as e:
                return self.finalize_response(request, e.response)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(
            request,
            response,
            *args,
            **kwargs
        )
        return self.response

    cls.dispatch = patched_dispatch
    return cls
