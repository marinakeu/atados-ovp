from ovp.apps.uploads.models import UploadedImage


def social_uid(backend, details, response, *args, **kwargs):
    return {
        "uid": "{}@{}".format(
            backend.get_user_id(
                details,
                response),
            kwargs["strategy"].request.channel)}


def get_avatar(backend, details, response, user=None, *args, **kwargs):
    url = None
    if backend.name == "facebook":
        url = "http://graph.facebook.com/{}/picture?type=large".format(
            response["id"])
    if backend.name == "google-oauth2":
        if response.get("picture", None):
            url = response["picture"]
    if url:
        if not user.avatar:
            avatar = UploadedImage.objects.create(
                absolute=True,
                object_channel=kwargs["strategy"].request.channel
            )
            UploadedImage.objects.filter(
                pk=avatar.pk).update(
                image=url,
                image_small=url,
                image_medium=url,
                image_large=url)
            user.avatar = avatar
            user.save()
