from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


class Forecast(models.Model):
    forecast_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, default=None, null=True, blank=True)
    is_auto_params_forecast = models.BooleanField()
    p_value = models.IntegerField()
    q_value = models.IntegerField()
    d_value = models.IntegerField()
    forecast_measures = ArrayField(
        models.FloatField()
    )
    n_count = models.IntegerField()
    dimensions = ArrayField(
        models.CharField(),
        default=None,
        null=True,
        blank=True,
    )
    measures = ArrayField(models.FloatField())
    visualization_type = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    unit = models.CharField(max_length=255, default=None, null=True, blank=True)