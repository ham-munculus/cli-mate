from rich.console import Console
from rich.panel import Panel
from rich.grid import Grid

# from rich.text import Text
# from rich.progress import Progress
from typing import Any
import logging

logger: logging.Logger = logging.getLogger(name=__name__)


class WeatherTUI:
    """Terminal UI for displaying weather data"""

    def __init__(self) -> None:
        self.console: Console = Console()

    def display_weather(self, weather_data: dict[str, Any]) -> None:
        """Display weather info in tui format"""
        location = weather_data["location"]
        periods = weather_data["periods"]

        # current conditions (first period)
        current = periods[0]
        self._display_current(location, current)

        # 12 hour forecast
        self._display_forecast(periods[1:])

    def _display_current(self, location: str, current: dict[str, Any]) -> None:
        """Display current weather conditions"""
        temp = current.get("temperature", "N/A")
        conditions = current.get("shortForecast", "N/A")
        wind_speed = current.get("windSpeed", "N/A")
        wind_direction = current.get("windDirection", "N/A")

        current_panel = (
            Panel(
                f"""[bold cyan]{location}[/bold cyan][yellow]{conditions}[/yellow]
                            Temperature: [bold]{temp}°{current.get("temperatureUnit", "F")}[/bold]
                            Wind: {wind_direction} {wind_speed}
                """
            ),
        )
        self.console.print(current_panel)

    def _display_forecast(self, periods: list[dict[str, Any]]) -> None:
        """Display 12-hour forecasts"""
        grid = Grid(padding=(0, 2))

        # add periods to grid (3 cols)
        for i, period in enumerate(periods[:12]):
            if i % 3 == 0 and i > 0:
                grid.add_row()

            time = period.get("name", "N/A")
            temp = period.get("temperature", "N/A")
            forecast = period.get("shortForecast", "N/A")
            wind = period.get("windSpeed", "N/A")

            cell = f"""[bold]{time}[/bold]
    {temp}°
    {forecast}
    Wind: {wind}"""

            grid.add_column(Panel(cell, border_style="green"))

        forecast_panel = Panel(
            grid,
            title="[bold]12-Hour Forecast[/bold]",
            border_style="green",
        )
        self.console.print(forecast_panel)

    def display_error(self, message: str) -> None:
        """Display error message"""
        error_panel = Panel(
            f"[red]{message}[/bold]",
            title="[bold red]Error[/bold red]",
            border_style="red",
        )
        self.console.print(error_panel)
