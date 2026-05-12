from django.urls import path

from app.api.views.auth import (
    EmailLoginView,
    LoginView,
    RefreshView,
    RegisterUserView,
    locations_cities_view,
    locations_provinces_view,
    locations_regions_view,
    logout_user_view,
    profile_me_view,
)

urlpatterns = [
    path("login/", LoginView.as_view(), name="api-login"),
    path("login-email/", EmailLoginView.as_view(), name="api-login-email"),
    path("register/", RegisterUserView.as_view(), name="api-register"),
    path("refresh/", RefreshView.as_view(), name="api-refresh"),
    path("logout/", logout_user_view, name="api-logout"),
    path("me/", profile_me_view, name="api-me"),
    path("locations/regions/", locations_regions_view, name="api-locations-regions"),
    path("locations/provinces/<int:region_id>/", locations_provinces_view, name="api-locations-provinces"),
    path("locations/cities/<int:province_id>/", locations_cities_view, name="api-locations-cities"),
]
