from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from .models import (Forecast)


class RegisterUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "email", "password")


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class AllForecastsSerializer(ModelSerializer):
    class Meta:
        model = Forecast
        fields = ("forecast_id", "title", "subtitle")

class ForecastSerializer(ModelSerializer):
    class Meta:
        model = Forecast
        fields = "__all__"
