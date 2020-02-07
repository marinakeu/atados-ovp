from django.contrib.auth import get_user_model
from ovp.apps.projects.models import Project
from ovp.apps.core.models import GoogleAddress
from django.db.models.signals import post_save
from channels.gdd.emails import GDDMail

User = get_user_model()

def send_email_to_manager(sender, *args, **kwargs):
  """
  Schedule task for 7 days after apply asking if user has received contact from organization
  """
  instance = kwargs["instance"]

  if instance.channel.slug == "gdd" and kwargs["created"] and not kwargs["raw"]:
    address = GoogleAddress(pk=instance.address.pk)
    country = address.address_components.filter(types__name='country').first()
    if country:
        country = country.short_name
    else:
        return None
    managers = User.objects.filter(groups__name="mng-{}".format(country.lower()))

    for manager in managers:
      GDDMail(manager, async_mail=True).sendProjectCreatedToCountryManager({'project': instance})
post_save.connect(send_email_to_manager, sender=Project)
