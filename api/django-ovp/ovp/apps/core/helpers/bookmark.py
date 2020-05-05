from django.db.models import Count, Case, Value, When, BooleanField


def annotate_bookmark(queryset, request=None):
    """
    Annotates a queryset with information
    about wether an object was bookmarked or not.

    Used on search viewsets.
    """
    if request and request.user.is_authenticated:
        qs = queryset.annotate(
            is_bookmarked=Count(
                Case(
                    When(bookmarks__user=request.user, then=True),
                    output_field=BooleanField()
                )
            )
        )
        return qs
    else:
        return queryset.annotate(is_bookmarked=Value(False, BooleanField()))
