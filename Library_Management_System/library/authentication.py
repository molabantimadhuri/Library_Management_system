from django.contrib.auth import get_user_model


class EmailBackend:
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = username or kwargs.get('email')
        if not email or not password:
            return None

        user_model = get_user_model()
        users = user_model.objects.filter(email__iexact=email)
        if users.count() != 1:
            return None

        user = users.first()
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None

    @staticmethod
    def user_can_authenticate(user):
        return getattr(user, 'is_active', True)
