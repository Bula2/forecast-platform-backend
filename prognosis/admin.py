from django.contrib import admin
from .models import (
    Forecast,
    Dataset,
    Result,
    Visualization,
)

admin.site.register(Dataset)
admin.site.register(Forecast)
admin.site.register(Visualization)
admin.site.register(Result)
