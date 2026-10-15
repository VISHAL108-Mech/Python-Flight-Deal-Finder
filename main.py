"""Check live flight prices across saved destinations and notify subscribers.

This script reads destination records from the spreadsheet, queries flight data,
compares results to the stored lowest prices, and sends an alert when a better
fare is found.
"""

from data_manager import DataManager
from pprint import pprint
from datetime import datetime, timedelta
from flight_search import FlightSearch
from flight_data import find_cheapest_flight
from notification_manager import NotificationManager

# Example rows used while populating the destination sheet for the first time.
# destination_delhi = data_manager.add_destination(city="Delhi",
#                                                  iata_code="DEL",
#                                                  price=10000,)
# destination_ahmedabad = data_manager.add_destination(city="Ahmedabad",
#                                                  iata_code="AMD",
#                                                  price=10000,)
# destination_kolkata = data_manager.add_destination(city="Kolkata",
#                                                  iata_code="CCU",
#                                                  price=10000,)

data_manager = DataManager()
sheet_data = data_manager.get_data()

user_data = data_manager.get_customer_emails()
user_email_list = [data["enterYourEmailAddress?"] for data in user_data]

# Search for flights starting tomorrow and compare them to the saved target prices.
tomorrow = datetime.now() + timedelta(days=1)
after_six_month = datetime.now() + timedelta(days=(6 * 30))

search = FlightSearch()
notification = NotificationManager()

departure_city = "IXZ"
city_name = "Port Blair"
i = 0

for city in sheet_data["prices"]:
    # pprint(f"Searching flights for {city["city"].title()}...")
    search_flight = search.check_flights(departure_city,
                                         city["iataCode"],
                                         departure_date=tomorrow,
                                         )

    flight_detail = find_cheapest_flight(search_flight).__dict__

    cheapest_flight = flight_detail["price"]
    sheet_price = sheet_data["prices"][i]["lowestPrice"]
    i += 1

    if cheapest_flight == "N/A":
        pprint(f"No direct flight to {city['city']}."
               f" Searching for indirect flights...")
        connected_flights = search.check_flights(
            departure_city,
            city["iataCode"],
            departure_date=tomorrow,
            is_direct=False,
        )
        low_cost_flight = find_cheapest_flight(connected_flights)
        low_cost_price = low_cost_flight.price
        print(
            f"Cheapest connected flight price is: INR {low_cost_price}/-")
        updated_sheet = data_manager.update_lowest_price(city["id"],
                                                         low_cost_price
                                                         )
        message = (f"Subject: Low price alert!✈️\n\nOnly ₹{low_cost_price} "
                   f"to fly from {city_name}({departure_city}) "
                   f"to {city["city"]}({city["iataCode"]}), "
                   f"with {low_cost_flight.stops} stop(s) "
                   f"on {tomorrow.date().strftime("%d-%m-%Y")}.")
        flight_alerts = notification.send_email(message=message,
                                                user_email=user_email_list)

    if  cheapest_flight < sheet_price and cheapest_flight != "N/A":
        updated_sheet = data_manager.update_lowest_price(city["id"],
                                                         cheapest_flight)
        messages = (f"Subject: Low price alert!✈️\n\nOnly ₹{cheapest_flight} "
                    f"to fly from {city_name}({departure_city}) "
                    f"to {city["city"]}({city["iataCode"]}), "
                    f"on {tomorrow.date().strftime("%d-%m-%Y")}.")
        flight_alerts = notification.send_notification(message=messages)

print("Email sent successfully!")
