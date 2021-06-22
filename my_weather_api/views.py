from .handlers import getWeatherForecast
from rest_framework import status

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import WeatherForecastDaySerializer

# Create your views here.

DATE_FORMAT = '%Y-%m-%d'

COUNTRY_CODES_TO_CAPITAL = {
    'CZ': 'Prague',
    'UK': 'London',
    'SK': 'Bratislava',
}

class GetWeather(APIView):
    serializer_class = WeatherForecastDaySerializer

    def get(self, request):
        
        country_code = request.GET.get('country_code')
        for_day = request.GET.get('date') # format YYYY-MM-DD
        force_api_call_query_param = request.GET.get('force_api_call')

        force_api_call = False
        if force_api_call_query_param != None and str(force_api_call_query_param).lower() in ['true', '1']:
            force_api_call = True

        if country_code == None or for_day == None:
            return Response({'Bad Request': 'Request must contain parameter country_code and parameter date.'}, status=status.HTTP_400_BAD_REQUEST)

        ret_data = getWeatherForecast(country_code, for_day, force_api_call)

        if ret_data['status'] == 'BAD_REQUEST':
            return Response({'Bad Request': ret_data['message']}, status=status.HTTP_400_BAD_REQUEST)
        
        elif ret_data['status'] == 'API_ERR':
            return Response({'Api Error': ret_data['message']}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # otherwise ret_json['status'] == 'OK'
        return Response(ret_data['data'], status=status.HTTP_200_OK)
