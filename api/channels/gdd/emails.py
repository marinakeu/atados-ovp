from ovp.apps.core.emails import BaseMail

class GDDMail(BaseMail):
  """
  This class is responsible for firing gdd specific emails
  """
  def __init__(self, user, async_mail=None):
    super(GDDMail, self).__init__(user.email, channel=user.channel.slug, async_mail=async_mail, locale=user.locale)

  def sendProjectCreatedToCountryManager(self, context={}):
    """
    Sent when user registers
    """
    return self.sendEmail('projectCreated-toCountryManager', 'A new project created at Good Deeds Day', context)
