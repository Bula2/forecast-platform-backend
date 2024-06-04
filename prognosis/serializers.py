from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from .models import (
    Result,
    Dataset,
    Forecast,
    Visualization,
)


class RegisterUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "email", "password")


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class DatasetSerializer(ModelSerializer):
    class Meta:
        model = Dataset
        fields = "__all__"


class ForecastSerializer(ModelSerializer):
    class Meta:
        model = Forecast
        fields = "__all__"


class VisualizationSerializer(ModelSerializer):
    class Meta:
        model = Visualization
        fields = "__all__"


class ResultSerializer(ModelSerializer):
    class Meta:
        model = Result
        fields = "__all__"


class CurrentResultSerializer(ModelSerializer):
    dataset = DatasetSerializer()
    forecast = ForecastSerializer()
    visualization = VisualizationSerializer()

    class Meta:
        model = Result
        fields = "__all__"
