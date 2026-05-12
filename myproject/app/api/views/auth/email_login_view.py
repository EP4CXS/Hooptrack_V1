from django.contrib.auth.models import User
from rest_framework import permissions, serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("username", None)
        self.fields["email"] = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist as exc:
            raise ValidationError({"detail": "No active account found with the given credentials"}) from exc
        if not user.is_active:
            raise ValidationError({"detail": "No active account found with the given credentials"})
        attrs["username"] = user.get_username()
        attrs.pop("email", None)
        return super().validate(attrs)


class EmailLoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EmailTokenObtainPairSerializer
