import typer
import logging
from cli_mate.weather import WeatherClient
from cli_mate.cache import WeatherCache
from cli_mate.tui import WeatherTUI

# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = typer.Typer(help="CLI-Mate: Terminal weather forecasts")

weather_client = WeatherClient()
cache = WeatherCache()
tui = WeatherTUI()


@app.command()
def weather(
    city: str = typer.Option(..., help="City name"),
    state: str = typer.Option(..., help="State abbreviation (e.g., CA. NY)"),
    no_cache: bool = typer.Option(
        False, "--no-cache", help="Skip cache and fetch data"
    ),
):
    """Get weather for a US city"""
    try:
        # try cache first
        if not no_cache:
            cached_data = cache.get(city, state)
            if cached_data:
                tui.display_weather(cached_data)
                return
        # fetch fresh data
        with typer.progressbar(length=1, label="Fetching weather...") as progress:
            weather_data = weather_client.get_weather(city, state)
            progress.update(1)

            # Cache it
            cache.set(city, state, weather_data)

            # display
            tui.display_weather(weather_data)
    except Exception as e:
        logger.error(f"Error: {e}")
        tui.display_error(str(e))
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Show version"""
    typer.echo("cli-mate v0.1.0")


if __name__ == "__main__":
    app()
