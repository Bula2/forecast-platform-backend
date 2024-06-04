import math
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
import itertools
from sklearn.metrics import mean_squared_error
import warnings
import numpy as np

warnings.filterwarnings("ignore")


def find_best_params(data):
    p_values = range(0, 3)  # Задаем диапазоны для p, d, q
    d_values = range(0, 3)
    q_values = range(0, 3)
    best_params = None
    best_mse = float("inf")  # Инициализируем значение наилучшей MSE

    # Составляем список всех возможных комбинаций параметров
    param_combinations = list(itertools.product(p_values, d_values, q_values))

    for param in param_combinations:
        try:
            # Создаем модель ARIMA с текущими параметрами
            model = ARIMA(data, order=param)

            # Обучаем модель на входных данных
            model_fit = model.fit()

            # Делаем прогноз на обучающей выборке
            forecast = model_fit.predict()

            # Вычисляем MSE для прогноза и исходных данных
            mse = mean_squared_error(data, forecast)

            # Обновляем лучшие параметры, если текущие MSE лучше
            if mse < best_mse:
                best_mse = mse
                best_params = param

        except Exception as e:
            print(f"Ошибка в обработке параметров {param}: {e}")

    return best_params


def make_forecast(dataIncome):
    data = dataIncome["measures"]
    if (dataIncome["is_auto_params_forecast"] == True):
        best_params = find_best_params(data)
    else:
        best_params = [
            dataIncome["p_value"],
            dataIncome["d_value"],
            dataIncome["q_value"],
        ]

    # Создаем модель ARIMA с параметрами (p, d, q)
    model = ARIMA(data, order=best_params)

    # Обучаем модель на входных данных
    model_fit = model.fit()

    # Делаем прогноз на n периода(-ов) вперед
    forecast = model_fit.forecast(steps=dataIncome["n_count"])
    result = list(map(float, forecast))

    # Возвращаем спрогнозированный массив значений
    return [result, best_params]


# print(
#     f"Прогноз: ${make_forecast( dataIncome={
#                 "measures": [
#     38498.6Ы,
#     23125.1,
#     43188.2,
#     23130.5,
#     45525.0,
#     28473.7,
#     37650.0,
#     29252.1,
#     31793.4,
#     27216.1,
#     19926.6,
#     30472.9,
#     23303.4,
#     29232.4,
#     20043.9,
#     25937.3,
#     19423.0,
#     26962.7,
#     20496.3,
#     34650.6,
#     17163.9,
#     37712.9,
#     16537.4,
#     # 43674.4,
# ],
#                 "p_value": p_value or 0,
#                 "q_value": q_value or 0,
#                 "d_value": d_value or 0,
#                 "is_auto_params_forecast": True,
#                 "n_count": int(1),
#             })}"
# )
