from django.core.cache import cache
from ovp.apps.channels.models import Channel
from ovp.apps.channels.defaults import DEFAULT_SETTINGS


def get_channel(slug):
    key = "channel-{}".format(slug)
    cache_ttl = 60
    result = cache.get(key)

    if not result:
        try:
            channel = Channel.objects.get(slug=slug)
        except Channel.DoesNotExist:
            result = None
        else:
            result = {
                "name": channel.name,
                "slug": channel.slug,
                "settings": {},
            }

            for setting in channel.channelsetting_channel.all():
                if setting.key in result["settings"]:
                    result["settings"][setting.key].append(setting.value)
                else:
                    result["settings"][setting.key] = [setting.value]

        cache.set(key, result, cache_ttl)

    return result


def get_channel_setting(slug, key):
    channel = get_channel(slug)

    if key in channel["settings"]:
        return channel["settings"][key]
    else:
        return DEFAULT_SETTINGS[key]
