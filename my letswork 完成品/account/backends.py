from django.contrib.auth.backends import BaseBackend
from account.models import Account_a

class CustomBackend(BaseBackend):
    def authenticate(self, request, a_no=None, password=None):
        try:
            user = Account_a.objects.get(a_no=a_no)
            if user.check_password(password) and user.is_active:
                return user
        except Account_a.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return Account_a.objects.get(pk=user_id)
        except Account_a.DoesNotExist:
            return None
