from django.core.management.base import BaseCommand, CommandError
from ...handlers import getWeatherForecast, COUNTRY_CODES_TO_CAPITAL
import json

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        # parser.add_argument('date', nargs='+', type=int)
        parser.add_argument('forecast_date', type=str, help='Date for which we want the forecast in format YYYY-MM-DD')
        cc_help = f"One of the permitted country codes: {', '.join(COUNTRY_CODES_TO_CAPITAL.keys())}"
        parser.add_argument('country_code', type=str, help=cc_help)

        parser.add_argument('-f', '--force-api-call', action='store_true', help='Force api call to weather api and refresh db entry')

    def handle(self, *args, **kwargs):
        forecast_date = kwargs['forecast_date']
        country_code = kwargs['country_code']
        force_api_call = kwargs['force_api_call']

        if force_api_call:
            ret_data = getWeatherForecast(country_code, forecast_date, force_api_call)
        else:
            ret_data = getWeatherForecast(country_code, forecast_date)

        if ret_data['status'] == 'OK':
            return json.dumps(ret_data['data'], indent=2)
        else:
            return json.dumps(ret_data['message'], indent=2)
        
        



        