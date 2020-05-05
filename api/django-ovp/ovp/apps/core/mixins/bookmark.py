from rest_framework import decorators
from rest_framework import response
from rest_framework import status
from rest_framework import permissions
from drf_yasg.utils import swagger_auto_schema


RESPONSES_DICT = {
    200: 'OK',
    400: 'Bad Request'
}


class BookmarkMixin(object):
    """
    This mixin allows for easily addition of bookmarking to a model.
    Currently it is applied to projects and organizations.

    It allows for:
        - Bookmarking a model
        - Unbookmarking a model
        - Retrieving list of bookmarked objects

    To use this mixin on your viewset it must declare two methods.
    .get_bookmark_model which returns a bookmark model which has an user
    foreign key and a related model foreign key.
    .get_bookmark_kwargs which returns a dictionary with data to create
    and filter a given bookmark. Usually it contains an instance to the
    related bookmark model.

    Such model may look something like this:
        class ProjectBookmark(AbstractBookmark):
        project = models.ForeignKey('Project', related_name='bookmarks')

    And the methods like:
        def get_bookmark_model(self):
        return ProjectBookmark

        def get_bookmark_kwargs(self):
        return {"project": self.get_object()}

    You also need to return the correct serializer for 'bookmarked' action
    on .get_serializer_class, as well as set self.permissions_classes =
    super().get_bookmark_permissions() for
    actions ['bookmark', 'unbookmark', 'bookmarked']

    """
    @swagger_auto_schema(method="POST", responses=RESPONSES_DICT)
    @decorators.action(["POST"], detail=True)
    def bookmark(self, request, *args, **kwargs):
        """
        Bookmark an object.
        """
        resp = {
            "detail": "Object sucesfully bookmarked.",
            "success": True
        }
        if self.get_bookmark_object():
            resp["detail"] = "Can't bookmark an object " \
                             "that has been already bookmarked."
            resp["success"] = False
            return response.Response(resp, status=status.HTTP_400_BAD_REQUEST)

        bookmark = self.get_bookmark_model()(
            user=request.user,
            **self.get_bookmark_kwargs()
        )
        bookmark.save(object_channel=request.channel)

        return response.Response(resp)

    @swagger_auto_schema(method="POST", responses=RESPONSES_DICT)
    @decorators.action(["POST"], detail=True)
    def unbookmark(self, request, *args, **kwargs):
        """
        Unbookmark an object.
        """
        resp = {
            "detail": "Object sucesfully unbookmarked.",
            "success": True
        }
        bookmark = self.get_bookmark_object()
        if not bookmark:
            resp["detail"] = "Can't unbookmark an object " \
                             "that it not bookmarked."
            resp["success"] = False
            return response.Response(resp, status=status.HTTP_400_BAD_REQUEST)

        bookmark.delete()

        return response.Response(resp)

    @swagger_auto_schema(method="GET", responses={200: 'OK'})
    @decorators.action(["GET"], detail=False)
    def bookmarked(self, request, *args, **kwargs):
        """
        Retrieve a list of bookmarked objects.
        """
        queryset = self.get_queryset().filter(
            bookmarks__user=request.user,
            bookmarks__channel__slug=request.channel
        )
        queryset = queryset.distinct('bookmarks__pk')
        queryset = queryset.order_by('-bookmarks__pk')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_bookmark_object(self):
        Bookmark = self.get_bookmark_model()
        bookmark_kwargs = self.get_bookmark_kwargs()

        try:
            return Bookmark.objects.get(
                user=self.request.user,
                channel__slug=self.request.channel,
                **bookmark_kwargs
            )
        except Bookmark.DoesNotExist:
            return None

    def get_bookmark_permissions(self):
        return (permissions.IsAuthenticated, )

    def get_bookmark_model(self):
        raise NotImplemented("Your viewset must override .get_bookmark_model")

    def get_bookmark_kwargs(self):
        raise NotImplemented("Your viewset must override .get_bookmark_kwargs")
