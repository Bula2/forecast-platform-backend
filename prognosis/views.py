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
from prognosis.models import Forecast, Dataset, Result, Visualization

from .serializers import (
    ForecastSerializer,
    DatasetSerializer,
    ResultSerializer,
    CurrentResultSerializer,
    RegisterUserSerializer,
    VisualizationSerializer,
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

        # Создаем запись о датасете
        dataset_serializer = DatasetSerializer(
            data={"dimensions": dimensions, "measures": measures}
        )
        dataset_serializer.is_valid(raise_exception=True)
        dataset_serializer.save()

        # Создаем запись о прогнозе
        forecast_serializer = ForecastSerializer(
            data={
                "is_auto_params_forecast": is_auto_params_forecast,
                "p_value": p_value,
                "q_value": q_value,
                "d_value": d_value,
                "forecast_measures": forecast_measures,
                "n_count": n_count,
            }
        )
        forecast_serializer.is_valid(raise_exception=True)
        forecast_serializer.save()

        # Создаем запись о визуализации
        visualization_serializer = VisualizationSerializer(
            data={
                "visualization_type": visualization_type,
                "color": color,
                "unit": unit,
            }
        )
        visualization_serializer.is_valid(raise_exception=True)
        visualization_serializer.save()

        final_result_serializer = ResultSerializer(
            data={
                "title": title,
                "subtitle": subtitle,
                "user": user.id,
                "dataset": dataset_serializer.data["dataset_id"],
                "forecast": forecast_serializer.data["forecast_id"],
                "visualization": visualization_serializer.data["visualization_id"],
            }
        )
        final_result_serializer.is_valid(raise_exception=True)
        final_result_serializer.save()

        return Response(
            {"result_id": final_result_serializer.data["result_id"]},
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
        user_id = request.GET.get("user_id", None)
        result_id = request.GET.get("result_id", None)
        result = Result.objects.filter(
            user_id=user_id
        ) & Result.objects.filter(result_id=result_id)
        result_serializer = CurrentResultSerializer(result, many=True)
        current_result = result_serializer.data

        return Response(current_result, status=status.HTTP_200_OK)

    except Result.DoesNotExist:
        return Response(
            {"details": "Информация о прогнозе не найдена."},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def GetAllForecasts(request):
    try:
        user_id = request.GET.get("user_id", None)
        results = Result.objects.filter(user_id=user_id)
        results_serializer = ResultSerializer(results, many=True)
        current_results = results_serializer.data
        current_results.reverse()

        return Response(current_results, status=status.HTTP_200_OK)

    except Result.DoesNotExist:
        return Response(
            {"details": "Информация о прогнозах не найдена."},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def DeleteForecast(request):
    try:
        # Получаем запись о прогнозе
        result_id = request.GET.get("result_id", None)
        result = Result.objects.get(result_id=result_id)

        # Получаем связанные сущности
        dataset_id = result.dataset_id
        forecast_id = result.forecast_id
        visualization_id = result.visualization_id

        # Удаляем запись о прогнозе
        result.delete()

        # Удаляем связанные сущности
        Dataset.objects.get(dataset_id=dataset_id).delete()
        Forecast.objects.get(forecast_id=forecast_id).delete()
        Visualization.objects.get(visualization_id=visualization_id).delete()

        return Response(
            {"details": "Прогноз успешно удален."},
            status=status.HTTP_204_NO_CONTENT,
        )

    except Result.DoesNotExist:
        return Response(
            {"details": "Прогноз не найден."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"details": f"Произошла ошибка при удалении: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
