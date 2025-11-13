import requests
from typing import cast
import logging

logger = logging.getLogger(name=__name__)


class WeatherClient:
    """Client for weather.gov API with support for geocoding."""

    BASE_URL: str = "https://api.weather.gov"
    GEO_URL: str = "https://nominatim.openstreetmap.org/search"

    def __init__(self, timeout: int = 5) -> None:
        self.timeout: int = timeout

    def _geocode(self, city: str, state: str) -> tuple[float, float]:
        """Convert city/state to lat/lon using OpenStreetMap Nominatim"""
        try:
            params: dict[str, str] = {
                "city": city,
                "state": state,
                "country": "USA",
                "format": "json",
            }
            response: requests.Response = requests.get(
                self.GEO_URL, params=params, timeout=self.timeout
            )
            response.raise_for_status()
            data: list[dict[str, str]] = cast(list[dict[str, str]], response.json())

            if not data:
                raise ValueError(f"Location not found: {city}, {state}")

            lat: float = float(data[0]["lat"])
            lon: float = float(data[0]["lon"])
            return lat, lon
        except requests.RequestException as e:
            raise RuntimeError(f"Geocoding failed: {e}")

    def _get_grid_point(self, lat: float, lon: float) -> dict[str, object]:
        """Get weather grid point from coordinates"""
        try:
            url: str = f"{self.BASE_URL}/points/{lat},{lon}"
            response: requests.Response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return cast(dict[str, object], response.json())
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to get grid point: {e}")

    def _fetch_forecast(self, forecast_url: str) -> dict[str, object]:
        """Fetch forecast data from URL"""
        try:
            response: requests.Response = requests.get(
                url=forecast_url, timeout=self.timeout
            )
            response.raise_for_status()
            return cast(dict[str, object], response.json())
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch forecast: {e}")

    def get_weather(
        self,
        city: str,
        state: str,
    ) -> dict[str, object]:
        """
        Get weather data for a city/state
        """
        try:
            lat, lon = self._geocode(city, state)
            grid_data: dict[str, object] = self._get_grid_point(lat, lon)
            properties: dict[str, object] = cast(
                dict[str, object], grid_data["properties"]
            )

            forecast_url: str = cast(str, properties["forecast"])
            forecast_data: dict[str, object] = self._fetch_forecast(forecast_url)
            forecast_properties: dict[str, object] = cast(
                dict[str, object], forecast_data["properties"]
            )
            periods: list[object] = cast(list[object], forecast_properties["periods"])[
                :13
            ]

            relative_location: dict[str, object] = cast(
                dict[str, object], properties["relativeLocation"]
            )

            return {
                "location": cast(
                    str,
                    cast(dict[str, object], relative_location["properties"])["city"],
                ),
                "periods": periods,
                "grid_id": cast(str, properties["gridId"]),
                "grid_point": {
                    "x": cast(int, properties["gridX"]),
                    "y": cast(int, properties["gridY"]),
                },
                "lat": lat,
                "lon": lon,
            }
        except (ValueError, RuntimeError, KeyError) as e:
            logger.error(f"Weather fetch error: {e}")
            raise
