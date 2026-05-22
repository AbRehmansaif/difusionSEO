from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class EmailAuthBackend(ModelBackend):
    """
    Authenticate using email address instead of username.
    The admin login form submits the value as 'username' field,
    so we intercept it and look up the user by email.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to find user by email (the 'username' field contains the email)
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            # Fall back to actual username lookup so superusers can still log in either way
            try:
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
