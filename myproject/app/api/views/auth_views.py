from django.contrib.auth.models import User
from rest_framework import permissions, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from app.api.serializers.auth_serializers import RegisterSerializer, UserSerializer

# Municipality -> Barangay -> City-style location lists for signup cascading selects.
LOCATIONS = {
    "regions": [
        {"id": 1, "name": "Cagwait"},
        {"id": 2, "name": "Bayabas"},
        {"id": 3, "name": "Marihatag"},
    ],
    "provinces": {
        1: [
            {"id": 11, "name": "Aras-asan"},
            {"id": 12, "name": "Bacolod"},
            {"id": 13, "name": "Bitaugan East"},
            {"id": 14, "name": "Bitaugan West"},
            {"id": 15, "name": "La Purisima"},
            {"id": 16, "name": "Lactudan"},
            {"id": 17, "name": "Mat-e"},
            {"id": 18, "name": "Poblacion"},
            {"id": 19, "name": "Tawagan"},
            {"id": 20, "name": "Tubo-tubo"},
            {"id": 21, "name": "Unidad"},
        ],
        2: [
            {"id": 22, "name": "Amag"},
            {"id": 23, "name": "Balete (Poblacion)"},
            {"id": 24, "name": "Cabugo"},
            {"id": 25, "name": "Cagbaoto"},
            {"id": 26, "name": "La Paz"},
            {"id": 27, "name": "Magobawok"},
            {"id": 28, "name": "Panaosawon"},
        ],
        3: [
            {"id": 29, "name": "Alegria"},
            {"id": 30, "name": "Amontay"},
            {"id": 31, "name": "Antipolo"},
            {"id": 32, "name": "Arorogan"},
            {"id": 33, "name": "Bayan"},
            {"id": 34, "name": "Mahaba"},
            {"id": 35, "name": "Mararag"},
            {"id": 36, "name": "Poblacion"},
            {"id": 37, "name": "San Antonio"},
            {"id": 38, "name": "San Isidro"},
            {"id": 39, "name": "San Pedro"},
            {"id": 40, "name": "Sta Cruz"},
        ],
    },
    "cities": {
        11: [{"id": 111, "name": "Aras-asan"}],
        12: [{"id": 112, "name": "Bacolod"}],
        13: [{"id": 113, "name": "Bitaugan East"}],
        14: [{"id": 114, "name": "Bitaugan West"}],
        15: [{"id": 115, "name": "La Purisima"}],
        16: [{"id": 116, "name": "Lactudan"}],
        17: [{"id": 117, "name": "Mat-e"}],
        18: [{"id": 118, "name": "Poblacion"}],
        19: [{"id": 119, "name": "Tawagan"}],
        20: [{"id": 120, "name": "Tubo-tubo"}],
        21: [{"id": 121, "name": "Unidad"}],
        22: [{"id": 122, "name": "Amag"}],
        23: [{"id": 123, "name": "Balete (Poblacion)"}],
        24: [{"id": 124, "name": "Cabugo"}],
        25: [{"id": 125, "name": "Cagbaoto"}],
        26: [{"id": 126, "name": "La Paz"}],
        27: [{"id": 127, "name": "Magobawok"}],
        28: [{"id": 128, "name": "Panaosawon"}],
        29: [{"id": 129, "name": "Alegria"}],
        30: [{"id": 130, "name": "Amontay"}],
        31: [{"id": 131, "name": "Antipolo"}],
        32: [{"id": 132, "name": "Arorogan"}],
        33: [{"id": 133, "name": "Bayan"}],
        34: [{"id": 134, "name": "Mahaba"}],
        35: [{"id": 135, "name": "Mararag"}],
        36: [{"id": 136, "name": "Poblacion"}],
        37: [{"id": 137, "name": "San Antonio"}],
        38: [{"id": 138, "name": "San Isidro"}],
        39: [{"id": 139, "name": "San Pedro"}],
        40: [{"id": 140, "name": "Sta Cruz"}],
    },
}


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


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def locations_regions_view(_request):
    return Response(LOCATIONS["regions"])


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def locations_provinces_view(_request, region_id):
    rows = LOCATIONS["provinces"].get(int(region_id), [])
    return Response(rows)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def locations_cities_view(_request, province_id):
    rows = LOCATIONS["cities"].get(int(province_id), [])
    return Response(rows)


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "success": True,
                "message": "Registration successful",
                "data": {
                    "user": UserSerializer(user).data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({"success": False, "message": "refresh token is required"}, status=400)
    token = RefreshToken(refresh_token)
    token.blacklist()
    return Response({"success": True, "message": "Logged out"}, status=200)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me_view(request):
    return Response({"success": True, "data": UserSerializer(request.user).data}, status=200)
