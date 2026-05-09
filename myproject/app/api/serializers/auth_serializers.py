from django.contrib.auth.models import User
from rest_framework import serializers

from app.models import UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    region_id = serializers.IntegerField(required=False, allow_null=True)
    province_id = serializers.IntegerField(required=False, allow_null=True)
    region_name = serializers.CharField(required=False, allow_blank=True)
    province_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "region_id",
            "province_id",
            "region_name",
            "province_name",
        ]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop("region_id", None)
        validated_data.pop("province_id", None)
        municipality = (validated_data.pop("region_name", "") or "").strip()
        barangay = (validated_data.pop("province_name", "") or "").strip()

        user = User.objects.create_user(**validated_data)
        organization = f"{municipality} Basketball League Ops" if municipality else ""
        UserProfile.objects.create(
            user=user,
            municipality=municipality,
            barangay=barangay,
            organization=organization,
            role="Administrator",
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    municipality = serializers.SerializerMethodField()
    barangay = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "municipality",
            "barangay",
            "organization",
            "is_staff",
            "is_superuser",
        ]

    def get_role(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.role if profile and profile.role else "Administrator"

    def get_municipality(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.municipality if profile else ""

    def get_barangay(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.barangay if profile else ""

    def get_organization(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.organization if profile else ""
