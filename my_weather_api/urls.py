from django.urls import path
from .views import GetWeather

urlpatterns = [
    path('weather-forecast', GetWeather.as_view()),
]
