class FlightData:
    """Simple container for a single flight option and its key details."""

    def __init__(self, lowest_price, departure, arrival, journey_date, stops,
                 return_date=None):
        """Store flight summary values for comparison and notification output."""
        self.price = lowest_price
        self.boarding_at = departure
        self.arrival_at = arrival
        self.departure_date = journey_date
        self.return_date = return_date
        self.stops = stops


def find_cheapest_flight(data, return_date=None):
    """Return the lowest-priced itinerary from the SerpAPI response payload."""
    best_flights = data.get("best_flights", [])
    other_flights = data.get("other_flights", [])
    all_flights = best_flights + other_flights
    return_date = return_date

    if all_flights is None or not best_flights and not other_flights:
        print("Sorry!, No Flights Available.")
        return FlightData("N/A", "N/A", "N/A",
                          "N/A", "N/A")

    first_flight = all_flights[0]
    lowest_price = first_flight["price"]
    departure = first_flight["flights"][0]["departure_airport"]["id"]
    arrival = first_flight["flights"][0]["arrival_airport"]["id"]
    journey_date = \
        first_flight["flights"][0]["departure_airport"]["time"].split(" ")[0]

    nr_stops = len(first_flight["flights"]) - 1

    cheapest_flight = FlightData(lowest_price, departure, arrival,
                                 journey_date,
                                 nr_stops)

    for flight in all_flights:
        try:
            price = flight["price"]
        except KeyError:
            print("No data available.")
            continue
        if price <= lowest_price:
            lowest_price = price
            departure = first_flight["flights"][0]["departure_airport"]["id"]
            arrival = first_flight["flights"][-1]["arrival_airport"]["id"]
            journey_date = \
                first_flight["flights"][0]["departure_airport"]["time"].split(
                    " ")[
                    0]
            nr_stops = len(first_flight["flights"]) - 1
            cheapest_flight = FlightData(lowest_price, departure, arrival,
                                         journey_date, nr_stops)
            print(f"Lowest price to {arrival} is INR {lowest_price}/-")

    return cheapest_flight
