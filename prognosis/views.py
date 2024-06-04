from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
import pandas as pd

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from prognosis.forecasts import make_forecast
from prognosis.models import Forecast

from .serializers import (
    ForecastSerializer,
    RegisterUserSerializer,
    AllForecastsSerializer,
)


# Получение информации о пользователе через token
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["username"] = user.username
        token["email"] = user.email
        token["first_name"] = user.first_name

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# Регистрация пользователя
@api_view(["POST"])
def RegisterUser(request):
    data = request.data
    try:
        username = data.get("username", data.get("email", ""))
        email = data.get("email")
        password = data.get("password")
        name = data.get("name", "")

        if (
            User.objects.filter(username=username).exists()
            or User.objects.filter(email=email).exists()
        ):
            return Response(
                {"details": "Пользователь с таким email или username уже существует"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Создаем нового пользователя
        user = User.objects.create(
            username=username,
            first_name=name,
            email=email,
            password=make_password(password),
        )

        serializer = RegisterUserSerializer(user, many=False)
        return Response(serializer.data)

    except Exception as e:
        return Response(
            {"details": f"Произошла ошибка: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def PostNewForecast(request):
    try:
        # Извлекаем данные из запроса
        user_id = request.data.get("user_id")
        title = request.data.get("title")
        subtitle = request.data.get("subtitle")
        file = request.data.get("file")
        is_auto_params_forecast = request.data.get("is_auto_params_forecast")
        p_value_init = request.data.get("p_value") or 0
        d_value_init = request.data.get("d_value") or 0
        q_value_init = request.data.get("q_value") or 0
        n_count = request.data.get("n_count") or 3
        visualization_type = request.data.get("visualization_type")
        color = request.data.get("color")
        unit = request.data.get("unit")

        # Получаем dimensions и measures
        if not file:
            return Response(
                {"details": "Файл не загружен."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        df = (
            pd.read_excel(file, engine="openpyxl")
            if file.name.endswith(".xlsx")
            else pd.read_csv(file)
        )

        if len(df.columns) == 2:
            dimensions = df.iloc[:, 0].astype(str).tolist()
            measures = df.iloc[:, 1].astype(float).tolist()
        elif len(df.columns) == 1:
            dimensions = None
            measures = df.iloc[:, 0].astype(float).tolist()

        forecast_measures, [p_value, q_value, d_value] = make_forecast(
            dataIncome={
                "measures": measures,
                "p_value": int(p_value_init),
                "q_value": int(q_value_init),
                "d_value": int(d_value_init),
                "is_auto_params_forecast": is_auto_params_forecast,
                "n_count": int(n_count),
            }
        )

        # Получаем пользователя
        user = User.objects.get(id=user_id)

        forecast_serializer = ForecastSerializer(
            data={
                "title": title,
                "subtitle": subtitle,
                "user": user.id,
                "dimensions": dimensions,
                "measures": measures,
                "is_auto_params_forecast": is_auto_params_forecast,
                "p_value": p_value,
                "q_value": q_value,
                "d_value": d_value,
                "forecast_measures": forecast_measures,
                "n_count": n_count,
                "visualization_type": visualization_type,
                "color": color,
                "unit": unit,
            }
        )
        forecast_serializer.is_valid(raise_exception=True)
        forecast_serializer.save()

        return Response(
            {"forecast_id": forecast_serializer.data["forecast_id"]},
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response(
            {"details": f"Произошла ошибка: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def GetCurrentForecast(request):
    try:
        forecast_id = request.GET.get("forecast_id", None)
        result = Forecast.objects.filter(forecast_id=forecast_id)
        forecast_serializer = ForecastSerializer(result, many=True)
        forecast = forecast_serializer.data

        return Response(forecast, status=status.HTTP_200_OK)

    except Forecast.DoesNotExist:
        return Response(
            {"details": "Информация о прогнозе не найдена."},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def GetAllForecasts(request):
    try:
        user_id = request.GET.get("user_id", None)
        forecasts = Forecast.objects.filter(user_id=user_id)
        all_forecast_serializer = AllForecastsSerializer(forecasts, many=True)
        all_forecasts = all_forecast_serializer.data
        all_forecasts.reverse()

        return Response(all_forecasts, status=status.HTTP_200_OK)

    except Forecast.DoesNotExist:
        return Response(
            {"details": "Информация о прогнозах не найдена."},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def DeleteForecast(request):
    try:
        # Получаем запись о прогнозе
        forecast_id = request.GET.get("forecast_id", None)
        forecast = Forecast.objects.get(forecast_id=forecast_id)

        # Удаляем запись о прогнозе
        forecast.delete()

        return Response(
            {"details": "Прогноз успешно удален."},
            status=status.HTTP_204_NO_CONTENT,
        )

    except Forecast.DoesNotExist:
        return Response(
            {"details": "Прогноз не найден."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"details": f"Произошла ошибка при удалении: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
