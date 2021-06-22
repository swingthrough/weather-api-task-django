from .serializers import WeatherForecastDaySerializer
from .models import WeatherForecastDay
from datetime import datetime, timedelta
import requests
from decouple import config
import json
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

def getWeatherForecast(country_code, for_day, force_api_call=False):

    ret_json_valid = {
        'status': 'OK',
        'data': {}
    }

    ret_json_bad_request = {
        'status': 'BAD_REQUEST',
        'message': '', 
    }

    ret_json_api_err = {
        'status': 'API_ERR',
        'message': '',
    }

    if country_code not in COUNTRY_CODES_TO_CAPITAL.keys():
        ret_json_bad_request['message'] = f"Value '{country_code}' for query parameter 'country_code' is invalid. Allowed values are {', '.join(COUNTRY_CODES_TO_CAPITAL.keys())}"
        return ret_json_bad_request
    
    if validateDateFormat(for_day) == False:
        ret_json_bad_request['message'] = f"Value '{for_day}' for query parameter 'date' is invalid. Must be a valid date in format YYYY-MM-DD"
        return ret_json_bad_request

    query_date = datetime.strptime(for_day, DATE_FORMAT).date()
    today = datetime.today().date()
    todayPlusTen = today + timedelta(days=10)

    if query_date < today:
        ret_json_bad_request['message'] = f"Value '{for_day}' for query parameter 'date' must be greater or equal to current date: {today.strftime(DATE_FORMAT)}"
        return ret_json_bad_request
    
    if query_date > todayPlusTen:
        ret_json_bad_request['message'] = f"Value '{for_day}' for query parameter 'date' cannot be larger than 10 days from now - furthest possible date for today is: {todayPlusTen.strftime(DATE_FORMAT)}"
        return ret_json_bad_request

    weatherForecastDayQuerySet = WeatherForecastDay.objects.filter(country_code=country_code, for_day=for_day)

    if force_api_call == False and len(weatherForecastDayQuerySet) > 0:
        data = WeatherForecastDaySerializer(weatherForecastDayQuerySet[0]).data
        avgtemp_c = float(data.get('average_temp_c'))

        forecast_json = {
            'forecast': getForecastSummaryFromTempC(avgtemp_c),
            'source': 'DB'
        }
        ret_json_valid['data'] = forecast_json
        return ret_json_valid
    else:
        url = WEATHER_API_URL.format(weather_api_key=WEATHER_API_KEY, city_name=COUNTRY_CODES_TO_CAPITAL.get(country_code), date=for_day)

        # TODO: handle potential exceptions of this API call
        try:
            response = requests.get(url)
            if response.status_code in [400, 401, 403]:
                json_response = response.json()
                ret_json_api_err['message'] = json_response['error']['message']
                return ret_json_api_err
            elif response.status_code >= 400:
                ret_json_api_err['message'] = 'Api Error'
                return ret_json_api_err


            json_response = response.json()
            avgtemp_c = json_response['forecast']['forecastday'][0]['day']['avgtemp_c']
            
            if len(weatherForecastDayQuerySet) > 0:
                forecast_json = {
                    'forecast': getForecastSummaryFromTempC(avgtemp_c),
                    'source': 'forced API call'
                }
                # update entry
                existingWeatherForecastDay = weatherForecastDayQuerySet[0]
                existingWeatherForecastDay.average_temp_c = avgtemp_c
                existingWeatherForecastDay.save(update_fields=['average_temp_c',])
            else:
                forecast_json = {
                    'forecast': getForecastSummaryFromTempC(avgtemp_c),
                    'source': 'API call'
                }
                # create entry
                newWeatherForecastDay = WeatherForecastDay(country_code=country_code, for_day=query_date, average_temp_c=avgtemp_c)
                newWeatherForecastDay.save()

            ret_json_valid['data'] = forecast_json
            return ret_json_valid
        except requests.exceptions.RequestException:
            ret_json_api_err['message'] = 'Api Error'
            return ret_json_api_err


        