from rest_framework import serializers
from .models import WeatherForecastDay

class WeatherForecastDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherForecastDay
        fields = ('id', 'country_code', 'for_day', 'average_temp_c',)
        # fields = '__all__'
        # fields = ('id', 'country_code', 'for_day')