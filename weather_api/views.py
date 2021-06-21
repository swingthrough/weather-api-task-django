from rest_framework import status

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import WeatherForecastDaySerializer
from .models import WeatherForecastDay
from datetime import datetime

# Create your views here.

# TODO: add coordinates to the tuple
COUNTRY_CODES_TO_COORDS = {
    'CZ': '...CZ',
    'UK': '...UK',
    'SK': '...SK',
}

# checks if the format is YYYY-MM-DD
def validateDate(date_text):
    try:
        if date_text != datetime.strptime(date_text, "%Y-%m-%d").strftime('%Y-%m-%d'):
            raise ValueError
        return True
    except ValueError:
        return False

class GetWeather(APIView):
    serializer_class = WeatherForecastDaySerializer
    # lookup_url_kwarg = 'code'

    def get(self, request):

        # TODO: add a parameter to invalidate old saved forecast and call external api again
        
        country_code = request.GET.get('country_code')
        for_day = request.GET.get('date') # format YYYY-MM-DD

        print('-------')
        print('country_code=', country_code)
        print('for_day=', for_day)
        print('for_day', )
        print('-------')

        if country_code == None or for_day == None:
            return Response({'Bad Request': 'Request must contain parameter country_code and parameter date.'}, status=status.HTTP_400_BAD_REQUEST)

        if country_code not in COUNTRY_CODES_TO_COORDS.keys():
            return Response({'Bad Request': f"Value '{country_code}' for query parameter 'country_code' is invalid. Allowed values are {', '.join(COUNTRY_CODES_TO_COORDS.keys())}"}, status=status.HTTP_400_BAD_REQUEST)

        if validateDate(for_day) == False:
            return Response({'Bad Request': f"Value '{for_day}' for query parameter 'date' is invalid. Must be a valid date in format YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: validate country_code
        # TODO: potentially combine validation of country_code and for_day with proper feedback

        
        
        weatherForecastDay = WeatherForecastDay.objects.filter(country_code=country_code, for_day=for_day)
        if len(weatherForecastDay) > 0:
            data = WeatherForecastDaySerializer(weatherForecastDay[0]).data
            return Response(data, status=status.HTTP_200_OK)
        else:
            # call api here
            # save to database
            return Response({"not yet": "functioning"}, status=status.HTTP_200_OK)

        
        # code = request.GET.get(self.lookup_url_kwarg)
        # if code != None:
        #     room = WeatherForecastDay.objects.filter(code=code)
        #     if len(room) > 0:
        #         data = RoomSerializer(room[0]).data
        #         data['is_host'] = self.request.session.session_key == room[0].host
        #         return Response(data, status=status.HTTP_200_OK)
        #     return Response({'Room not found': 'Invalid Room Code.'}, status=status.HTTP_404_NOT_FOUND)
        
        # return Response({'Bad Request': 'Code parameter not found in request'}, status=status.HTTP_400_BAD_REQUEST)