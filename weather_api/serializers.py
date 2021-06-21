from rest_framework import serializers
from .models import WeatherForecastDay

class WeatherForecastDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherForecastDay
        # fields = ('id', 'country_code', 'for_day', 'created_at')
        fields = '__all__'