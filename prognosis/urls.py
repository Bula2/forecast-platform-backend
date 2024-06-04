from django.urls import path
from prognosis import views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path("token/", views.MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("user/add/", views.RegisterUser, name="RegisterUser"),
    path("forecast/add/", views.PostNewForecast, name="PostNewForecast"),
    path(
        "forecast/get/current/",
        views.GetCurrentForecast,
        name="GetCurrentForecast",
    ),
    path(
        "forecast/get/all/",
        views.GetAllForecasts,
        name="GetAllForecasts",
    ),
    path(
        "forecast/delete/current/",
        views.DeleteForecast,
        name="DeleteForecast",
    ),
]
