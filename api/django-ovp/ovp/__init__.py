
def get_core_apps(disable_external=False):
    """ Get core ovp apps list.

    Returns:
      list: A list with all ovp apps to be appended to INSTALLED_APPS on settings.py
    """
    EXTERNAL_APPS = [
        "haystack",
        "vinaigrette",
        "corsheaders",
        "jet",
        "jet.dashboard",
        "martor",
    ]

    CORE_APPS = [
        "ovp.apps.core",
        "ovp.apps.admin",
        "ovp.apps.uploads",
        "ovp.apps.users",
        "ovp.apps.projects",
        "ovp.apps.organizations",
        "ovp.apps.faq",
        "ovp.apps.search",
        "ovp.apps.channels",
        "ovp.apps.catalogue",
        "ovp.apps.items",
        "ovp.apps.ratings",
        "ovp.apps.gallery",
        "ovp.apps.donations",
        "ovp.apps.digest",
    ]

    if disable_external:
        return CORE_APPS
    return CORE_APPS + EXTERNAL_APPS
