from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


class Dataset(models.Model):
    dataset_id = models.AutoField(primary_key=True)
    dimensions = ArrayField(
        models.CharField(max_length=255, default=None, null=True, blank=True),
        default=None,
        null=True,
        blank=True,
    )
    measures = ArrayField(models.FloatField(default=None, null=True, blank=True))


class Forecast(models.Model):
    forecast_id = models.AutoField(primary_key=True)
    is_auto_params_forecast = models.BooleanField(default=False, null=True, blank=True)
    p_value = models.IntegerField(default=None, null=True, blank=True)
    q_value = models.IntegerField(default=None, null=True, blank=True)
    d_value = models.IntegerField(default=None, null=True, blank=True)
    forecast_measures = ArrayField(
        models.FloatField(default=None, null=True, blank=True)
    )
    n_count = models.IntegerField(default=3, null=True, blank=True)


class Visualization(models.Model):
    visualization_id = models.AutoField(primary_key=True)
    visualization_type = models.CharField(max_length=255)
    color = models.CharField(max_length=255, default=None, null=True, blank=True)
    unit = models.CharField(max_length=255, default=None, null=True, blank=True)


class Result(models.Model):
    result_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, default=None, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    forecast = models.ForeignKey(
        Forecast, on_delete=models.CASCADE, default=None, null=True, blank=True
    )
    visualization = models.ForeignKey(Visualization, on_delete=models.CASCADE)
