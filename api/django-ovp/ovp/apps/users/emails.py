from ovp.apps.core.emails import BaseMail


class UserMail(BaseMail):
    """
    This class is responsible for firing emails for Users
    """

    def __init__(self, user, async_mail=None):
        super().__init__(
            user.email,
            channel=user.channel.slug,
            async_mail=async_mail,
            locale=user.locale)

    def sendWelcome(self, context={}):
        """
        Sent when user registers
        """
        return self.sendEmail('welcome', 'Welcome', context)

    def sendLogin(self, context={}):
        """
        Sent when user registers
        """
        return self.sendEmail('login', 'Login', context)

    def sendRecoveryToken(self, context):
        """
        Sent when volunteer requests recovery token
        """
        return self.sendEmail('recoveryToken', 'Password recovery', context)

    def sendMessageToAnotherVolunteer(self, context):
        """
        Sent when volunteer make contact with another volunteer
        """
        return self.sendEmail(
            'messageToVolunteer',
            'Volunteer Message',
            context)

    def sendUpdateEmail(self, context):
        """
        Sent when volunteer requests reset email
        """
        return self.sendEmail('updateEmail', 'Update Email', context)

    def sendEmailVerification(self, context):
        """
        Sent when email verification token is created
        """
        return self.sendEmail(
            'emailVerification',
            'Verify your email',
            context)
