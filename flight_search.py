"""Flight search wrapper for querying the SerpAPI Google Flights endpoint."""

import os
import requests_cache
from dotenv import load_dotenv

load_dotenv()

# Base URL for the SerpAPI flights engine, loaded from environment variables.
SERP_ENDPOINT = os.getenv("SERP_ENDPOINT")


class FlightSearch:
    """Query Google Flights data for a route using SerpAPI."""

    def __init__(self):
        """Load the API key required to access SerpAPI."""
        self.SERP_KEY = os.getenv("SERP_KEY")

    def check_flights(self, from_city_code, to_city_code, departure_date,
                      return_date=None, is_direct=True):
        """Return raw JSON flight results for the requested route and dates."""
        parameters = {
            "engine": "google_flights",
            "departure_id": from_city_code,
            "arrival_id": to_city_code,
            "outbound_date": departure_date.strftime("%Y-%m-%d"),
            # Return date is intentionally left out for the current implementation.
            # "return_date": return_date.strftime("%Y-%m-%d"),
            "type": "2",
            "adults": "1",
            "currency": "INR",
            "stops": "0",
            "api_key": self.SERP_KEY,
        }

        # When is_direct is True, request results limited to non-stop itineraries.
        if is_direct:
            parameters["stops"] = "1"

        try:
            session = requests_cache.CachedSession("flight_search")
            r = session.get(url=SERP_ENDPOINT, params=parameters)
            # print(r.status_code)
            data = r.json()
            return data
        except r.raise_for_status as error:
            print(error)
