"""Helpers for reading and updating the flight sheet and customer list."""

import requests
# import requests_cache
import os
from dotenv import load_dotenv

load_dotenv()


class DataManager:
    """Read and update destination pricing and customer records stored in Sheety."""

    def __init__(self):
        """Load the API and user endpoints from environment variables."""
        self.API_ENDPOINT = os.getenv("SHEET_ENDPOINT")
        self.USER_ENDPOINT = os.getenv("SHEETY_USER_ENDPOINT")
        # self.PASSWORD = os.getenv("FLIGHT_AUTH_PASS")
        # self.headers = {
        #     "Authorization": self.PASSWORD
        # }

    def get_data(self):
        """Fetch all destination rows from the Sheety spreadsheet."""
        try:
            # session = requests_cache.CachedSession("flight_cache",
            #                                        expire_after=3600)
            r = requests.get(url=f"{self.API_ENDPOINT}")
            r.raise_for_status()
            data = r.json()
            return data
        except r.raise_for_status as error:
            return error

    def update_lowest_price(self, row_id, new_price):
        """Update the stored lowest price for a specific destination row."""
        try:
            update_price = {"price": {"lowestPrice": new_price}}
            r = requests.put(url=f"{self.API_ENDPOINT}/{row_id}",
                             json=update_price)
            return r.json()
        except KeyError as e:
            print(e)

    def add_destination(self, city, iata_code, price):
        """Add a new destination row with its city, IATA code, and target price."""
        add_data = {"price": {
            "city": city,
            "iataCode": iata_code,
            "lowestPrice": price,
        }
        }

        r = requests.post(url=self.API_ENDPOINT, json=add_data)
        data = r.json()
        return data

    def get_customer_emails(self):
        """Fetch the list of subscribed customer records and return their details."""
        r = requests.get(url=self.USER_ENDPOINT)
        r.raise_for_status()
        user_data = r.json()
        user_data = user_data["users"]
        return user_data
