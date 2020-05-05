from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import response
from rest_framework import status
from rest_framework.decorators import action
from ovp.apps.core.models import Post


class PostCreateMixin:
    """
    Classes extending this mixin should handle
    'post' and 'post_patch' actions on their
    .get_permissions() and .get_serializer_class()
    """
    @swagger_auto_schema(method="POST", responses={200: "OK"})
    @action(['POST'], detail=True, url_path='post')
    def post(self, request, slug, pk=None):
        """
        Create a post for an object.
        """
        data = request.data
        user = request.user
        obj = self.get_object()

        data['user'] = user.pk

        serializer = self.get_serializer_class()(
            data=data,
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        obj.posts.add(serializer.instance)
        obj.save()

        return response.Response(serializer.data)

    @action(['PATCH', 'DELETE'], detail=True, url_path=r'post/(?P<post_id>[\w-]+)')
    def post_patch_delete(self, request, slug, post_id):
        """
        Update and delete a post for an object.
        """
        data = request.data
        obj = self.get_object()
        post = self.get_post_object(obj.posts, post_id)

        if request.method == "DELETE":
            post.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = self.get_serializer_class()(
                post,
                data=request.data,
                partial=True,
                context=self.get_serializer_context()
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        # pragma: no cover
        if getattr(post, '_prefetched_objects_cache', None):
            post = self.get_object()
            serializer = self.get_serializer(post)

        return response.Response(serializer.data)

    def get_post_object(self, qs, pk):
        try:
            return qs.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404
