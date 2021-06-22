from rest_framework import status

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import WeatherForecastDaySerializer
from .models import WeatherForecastDay
from datetime import datetime, timedelta
import requests
from decouple import config

# Create your views here.

DATE_FORMAT = '%Y-%m-%d'

COUNTRY_CODES_TO_CAPITAL = {
    'CZ': 'Prague',
    'UK': 'London',
    'SK': 'Bratislava',
}

WEATHER_API_KEY = config('WEATHER_API_KEY', default='')

WEATHER_API_URL = "http://api.weatherapi.com/v1/forecast.json?key={weather_api_key}&q={city_name}&dt={date}&days=1&aqi=no&alerts=no"

# checks if the format is YYYY-MM-DD
def validateDateFormat(date_text):
    try:
        if date_text != datetime.strptime(date_text, DATE_FORMAT).strftime(DATE_FORMAT):
            raise ValueError
        return True
    except ValueError:
        return False

def getForecastSummaryFromTempC(temp_c):
    if temp_c > 20:
        return "good"
    elif temp_c >= 10:
        return "soso"
    else:
        return "bad"

class GetWeather(APIView):
    serializer_class = WeatherForecastDaySerializer

    def get(self, request):

        # TODO: add a parameter to invalidate old saved forecast and call external api again
        
        country_code = request.GET.get('country_code')
        for_day = request.GET.get('date') # format YYYY-MM-DD

        if country_code == None or for_day == None:
            return Response({'Bad Request': 'Request must contain parameter country_code and parameter date.'}, status=status.HTTP_400_BAD_REQUEST)

        if country_code not in COUNTRY_CODES_TO_CAPITAL.keys():
            return Response({'Bad Request': f"Value '{country_code}' for query parameter 'country_code' is invalid. Allowed values are {', '.join(COUNTRY_CODES_TO_CAPITAL.keys())}"}, status=status.HTTP_400_BAD_REQUEST)

        if validateDateFormat(for_day) == False:
            return Response({'Bad Request': f"Value '{for_day}' for query parameter 'date' is invalid. Must be a valid date in format YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        
        query_date = datetime.strptime(for_day, DATE_FORMAT).date()
        today = datetime.today().date()
        todayPlusTen = today + timedelta(days=10)
        
        if query_date < today:
            return Response({'Bad Request': f"Value '{for_day}' for query parameter 'date' must be greater or equal to current date: {today.strftime(DATE_FORMAT)}"}, status=status.HTTP_400_BAD_REQUEST)
        if query_date > todayPlusTen:
            return Response({'Bad Request': f"Value '{for_day}' for query parameter 'date' cannot be larger than 10 days from now - furthest possible date for today is: {todayPlusTen.strftime(DATE_FORMAT)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: potentially combine validation of country_code and for_day with proper feedback
        
        weatherForecastDay = WeatherForecastDay.objects.filter(country_code=country_code, for_day=for_day)
        if len(weatherForecastDay) > 0:
            data = WeatherForecastDaySerializer(weatherForecastDay[0]).data
            avgtemp_c = float(data.get('average_temp_c'))

            forecast_json = {
                'forecast': getForecastSummaryFromTempC(avgtemp_c),
                'source': 'database'
            }
            return Response(forecast_json, status=status.HTTP_200_OK)
        else:
            url = WEATHER_API_URL.format(weather_api_key=WEATHER_API_KEY, city_name=COUNTRY_CODES_TO_CAPITAL.get(country_code), date=for_day)

            # TODO: handle potential exceptions of this API call
            response = requests.get(url)

            json_response = response.json()
            avgtemp_c = json_response['forecast']['forecastday'][0]['day']['avgtemp_c']

            forecast_json = {
                'forecast': getForecastSummaryFromTempC(avgtemp_c),
                'source': 'API call'
            }
            newWeatherForecastDay = WeatherForecastDay(country_code=country_code, for_day=query_date, average_temp_c=avgtemp_c)
            newWeatherForecastDay.save()

            return Response(forecast_json, status=status.HTTP_200_OK)
