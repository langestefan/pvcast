"""Test the weather module."""
from __future__ import annotations

import pytest
import requests
from const import LOC_AUS, LOC_EUW, LOC_USW
from pandas import DataFrame
from pvlib.location import Location
from pvcast.weather.weather import WeatherAPI, WeatherAPIError, WeatherAPIErrorTooManyReq, WeatherAPIErrorWrongURL
import mock


# mock for WeatherAPI class
class MockWeatherAPI(WeatherAPI):
    """Mock the WeatherAPI class."""

    code: int = 200  # default http return code

    def _process_data(self, response: requests.Response) -> DataFrame:
        """Get weather data from API response."""
        return DataFrame()

    def _url_formatter(self) -> str:
        """Format the url with lat, lon, alt."""
        return self._url


class TestWeather:
    """Test the weather module."""

    @pytest.fixture(params=[LOC_EUW, LOC_USW, LOC_AUS])
    def weather_obj(self, request):
        """Get a weather API object."""

        lat = request.param[0]
        lon = request.param[1]
        alt = request.param[2]
        tz = request.param[3]

        return MockWeatherAPI(location=Location(lat, lon, tz, alt))

    @pytest.fixture(params=[404, 429, 500])
    def weather_obj_error(self, request):
        """Get a weather API object with an error."""
        url_base = "http://httpbin.org/status/"

        def httpbin_url_formatter(self) -> str:
            return f"{url_base}{request.param}"

        # mock _url_formatter() function
        with mock.patch.object(MockWeatherAPI, "_url_formatter", new=httpbin_url_formatter):
            obj = MockWeatherAPI(location=Location(0, 0, "UTC", 0))
            obj.code = request.param
            return obj

    def test_get_weather_obj(self, weather_obj):
        """Test the get_weather function."""
        assert isinstance(weather_obj, WeatherAPI)
        assert isinstance(weather_obj.location, Location)

    def test_error_handling(self, weather_obj_error):
        """Test the get_weather error handling function."""
        error_dict = {
            404: WeatherAPIErrorWrongURL,
            429: WeatherAPIErrorTooManyReq,
            500: WeatherAPIError,
        }

        with pytest.raises(error_dict[weather_obj_error.code]):
            weather_obj_error._api_request_if_needed()
