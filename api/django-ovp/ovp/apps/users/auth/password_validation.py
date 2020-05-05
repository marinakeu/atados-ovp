from django.contrib.auth.password_validation import MinimumLengthValidator


class CustomMinimumLengthValidator(MinimumLengthValidator):
    """
    Customized the class base validate whether the password
    is of a minimum length equal a 6.
    """
    def __init__(self, min_length=6):
        super().__init__(min_length)
