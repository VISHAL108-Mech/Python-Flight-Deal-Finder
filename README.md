# ✈️ Flight Deals Finder

A Python automation that watches flight prices to a list of destinations and emails every subscribed user the moment it finds a deal cheaper than the current lowest recorded price — built around a Google Sheet acting as a lightweight database, live flight data from SerpApi's Google Flights engine, and Gmail for delivery.

> Set your destinations and target prices once in a spreadsheet. The script checks live prices, updates the sheet when it finds something cheaper, and emails everyone subscribed — no manual price-checking required.

---

## 🎮 Demo

A real run against four tracked destinations — note how it automatically falls back to an indirect search when no direct flight is found, and only emails when a genuinely new low price is recorded:

<img width="400" height="300" alt="Screenshot 2026-10-05 162917" src="https://github.com/user-attachments/assets/62bef6e0-2844-49f6-8a3d-ff1e92d1f567" />
<img width="400" height="300" alt="Screenshot 2026-10-05 162709" src="https://github.com/user-attachments/assets/a1ac9dbd-6c98-4159-a8ed-2e615ced4bf0" />
<img width="400" height="300" alt="Screenshot 2026-10-05 162500" src="https://github.com/user-attachments/assets/87adf87c-4381-487e-9f7e-08cffd9c18d7" />
<img width="400" height="300" alt="Screenshot 2026-10-05 162430" src="https://github.com/user-attachments/assets/36ed7d7f-6274-4189-b3a8-7d67ddc17373" />

---

## ✨ Features

- 📊 **Google Sheets as a database** — destinations, IATA codes, and lowest recorded prices are managed entirely in a spreadsheet via the Sheety API, no SQL setup needed.
- ✈️ **Live flight search** powered by SerpApi's Google Flights engine, checking real prices for every destination on the list.
- 📉 **Automatic price-drop detection** — compares each live result against the previously recorded lowest price and only acts when a genuinely better deal appears.
- 🔄 **Self-updating records** — the moment a new low price is found, it's written straight back to the Google Sheet via a `PUT` request.
- 🔁 **Indirect flight fallback** — if no direct flight exists for a route, the script automatically retries the search allowing connecting flights.
- 📧 **Mass email notifications** — every subscribed user (pulled from a second Sheety-powered "users" sheet) gets notified automatically when a deal is found.
- 📝 **Public sign-up form** — a Google Form lets anyone subscribe with their name and email; responses flow straight into the Google Sheet that powers the notification list, with zero manual entry.
- ⚡ **HTTP response caching** via `requests_cache` to avoid hammering the flight search API with repeat requests.

---

## 🛠️ Tech Stack

| Category | Tool / Concept |
|---|---|
| Language | Python 3 |
| Flight Data | [SerpApi](https://serpapi.com/) — Google Flights search engine |
| Spreadsheet-as-Database | [Sheety](https://sheety.co/) — turns a Google Sheet into a REST API |
| HTTP Requests | `requests`, `requests_cache` |
| Email | `smtplib` (standard library) — SMTP + TLS email delivery |
| Secrets Management | `python-dotenv` |
| Paradigm | Object-Oriented Programming — separate classes for data, search, and notifications |
| Core Concepts | REST API integration (GET/POST/PUT), JSON parsing, date handling, batch email delivery |

---

## 📂 Project Structure

```
Flight Deals Finder/
│
├── main.py                  # Entry point — orchestrates the full price-check workflow
├── data_manager.py           # DataManager — reads/writes the Google Sheet via Sheety
├── flight_search.py          # FlightSearch — queries SerpApi for live flight prices
├── flight_data.py             # FlightData class + logic to find the cheapest result
├── notification_manager.py    # NotificationManager — sends email alerts via Gmail
├── experiment.ipynb            # Scratch notebook for prototyping/testing API calls outside the main pipeline
├── .env                          # API keys, Sheety endpoints, and Gmail credentials (never committed)
├── .gitignore                     # Excludes .env and local cache databases from version control
└── README.md
```

Each module owns one responsibility — `data_manager.py` only talks to the spreadsheet, `flight_search.py` only talks to SerpApi, `notification_manager.py` only sends email — with `main.py` acting purely as the orchestrator that ties them together.

> 📌 Note: `requests_cache` generates local `.sqlite` cache files (e.g. `flight_cache.sqlite`, `flight_search.sqlite`) at runtime. These are environment-specific and should be listed in `.gitignore` rather than committed to the repo.

---

## 🗂️ Data Sources

### The sign-up form
Subscribers join the notification list through a simple public Google Form — just first name, last name, and email. No account or login required.

| Field |
|---|
| Enter your first name? |
| Enter your last name? |
| Enter your email address? |

Every submission lands automatically in a **Form_Responses** tab of the same Google Sheet, which Sheety exposes as `SHEETY_USER_ENDPOINT` for `get_customer_emails()` to read.

### The tracked destinations sheet
A separate tab holds the destinations being watched, each with its IATA code and the lowest price recorded so far — this is what `data_manager.py` reads from and writes back to.

| City | IATA Code | Lowest Price |
|---|---|---|
| Mumbai | BOM | 10637 |
| Delhi | DEL | 16681 |
| Ahmedabad | AMD | 13524 |
| Kolkata | CCU | 7735 |

This sheet is the single source of truth the whole app runs on — add a new row here and the script starts tracking that destination on the next run, no code changes required.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.x installed
- A Google Sheet set up with [Sheety](https://sheety.co/) (one sheet for destinations/prices, one for subscribed user emails)
- A free or paid [SerpApi](https://serpapi.com/) account and API key
- `requests`, `requests_cache`, and `python-dotenv` — install via pip:

```bash
pip install requests requests_cache python-dotenv
```

### Setup

**1. Create your `.env` file** in the project root:

```
SHEET_ENDPOINT=your_sheety_prices_endpoint
SHEETY_USER_ENDPOINT=your_sheety_users_endpoint
SERP_ENDPOINT=https://serpapi.com/search
SERP_KEY=your_serpapi_key
SMTP_GMAIL_ID=your_email@gmail.com
SMTP_GMAIL_PASSWORD=your_app_password
```

> ⚠️ Use a [Gmail App Password](https://myaccount.google.com/apppasswords), not your real Gmail password. Add `.env` to your `.gitignore` so it's never pushed to GitHub.

**2. Set up your Google Sheet** with a destinations tab (`City`, `IATA Code`, `Lowest Price` columns) and a `Form_Responses` tab for subscribers. Create a Google Form with first name, last name, and email fields, and link its responses to the `Form_Responses` tab — see [Data Sources](#️-data-sources) below for the exact structure.

### Run it
```bash
python main.py
```

### Automate it
Since this is meant to run unattended, schedule it with cron, Windows Task Scheduler, GitHub Actions, or PythonAnywhere's Scheduled Tasks — daily or a few times a week is typical for price-tracking.

---

## 🧩 How It Works

### 1. Reading Destinations & Subscribers from the Sheet
`DataManager` wraps every spreadsheet interaction — fetching the destination list, pulling subscriber emails, and later writing updated prices back — so the rest of the app never talks to Sheety directly.

```python
class DataManager:
    """Read and update destination pricing and customer records stored in Sheety."""

    def __init__(self):
        """Load the API and user endpoints from environment variables."""
        self.API_ENDPOINT = os.getenv("SHEET_ENDPOINT")
        self.USER_ENDPOINT = os.getenv("SHEETY_USER_ENDPOINT")

    def get_data(self):
        """Fetch all destination rows from the Sheety spreadsheet."""
        try:
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

    def get_customer_emails(self):
        """Fetch the list of subscribed customer records and return their details."""
        r = requests.get(url=self.USER_ENDPOINT)
        r.raise_for_status()
        user_data = r.json()
        user_data = user_data["users"]
        return user_data
```

### 2. Searching for Live Flight Prices
`FlightSearch` queries SerpApi's Google Flights engine for a given route and date, wrapping the request in a cached session so repeat lookups don't waste API calls.

```python
def check_flights(self, from_city_code, to_city_code, departure_date,
                  return_date=None, is_direct=True):
    """Return raw JSON flight results for the requested route and dates."""
    parameters = {
        "engine": "google_flights",
        "departure_id": from_city_code,
        "arrival_id": to_city_code,
        "outbound_date": departure_date.strftime("%Y-%m-%d"),
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
        data = r.json()
        return data
    except r.raise_for_status as error:
        print(error)
```

### 3. Finding the Cheapest Option
`find_cheapest_flight()` scans through every flight SerpApi returned (combining both "best" and "other" results) and keeps track of whichever has the lowest price. The final destination is read from the **last** leg of the itinerary, so connecting flights report where the traveler actually lands rather than the first layover.

```python
def find_cheapest_flight(data, return_date=None):
    """Return the lowest-priced itinerary from the SerpAPI response payload."""
    best_flights = data.get("best_flights", [])
    other_flights = data.get("other_flights", [])
    all_flights = best_flights + other_flights

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
```

### 4. Comparing Prices & Deciding Whether to Alert
`main.py` is the orchestrator — for every destination in the sheet, it searches live prices, compares against the recorded lowest, falls back to indirect flights if no direct option exists, and triggers an email when a genuinely cheaper deal is found.

```python
for city in sheet_data["prices"]:
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
```

### 5. Sending the Alerts
`NotificationManager` has two delivery modes — one for a quick personal notification, and one for broadcasting the same deal to every subscribed customer.

```python
class NotificationManager:
    """Send low-price flight alerts using the configured Gmail SMTP account."""

    def __init__(self):
        """Store the Gmail credentials used by all outgoing email alerts."""
        self.email = EMAIL
        self.password = PASSWORD

    def send_notification(self, message):
        """Send a single message to the configured sender address."""
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=self.email, password=self.password)
            connection.sendmail(
                from_addr=self.email,
                to_addrs=self.email,
                msg=message.encode("utf-8"),
            )

    def send_email(self, message, user_email):
        """Send one alert to each email address in a user list."""
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=self.email, password=self.password)
            for email in user_email:
                connection.sendmail(
                    from_addr=self.email,
                    to_addrs=email,
                    msg=message.encode("utf-8"),
                )
```

---

## 📚 What This Project Demonstrates

- Orchestrating multiple independent modules (data, search, notification) into one coherent workflow
- Using a spreadsheet as a lightweight, no-setup database via a REST API wrapper (Sheety)
- Integrating a third-party search API (SerpApi) and parsing deeply nested JSON results
- Implementing fallback logic (direct → indirect search) for a more resilient user experience
- Batch-sending personalized notifications to a list of subscribers
- Reducing redundant API calls with HTTP response caching
- Writing self-documenting code with module-, class-, and method-level docstrings

---

## 🔮 Future Improvements

> 🐞 This is a learning project, so there may still be bugs and rough edges — feedback and fixes are welcome.

- [ ] Tighten error handling so failed API requests are caught cleanly and don't crash the run
- [ ] Make the price comparison in `main.py` safe when no direct flight is found
- [ ] Pull every flight detail (departure, date, stops) from the same itinerary as the price
- [ ] Email about indirect flights only when the price is genuinely lower than the stored one
- [ ] Add return-flight search, retry logic for transient API failures, and logging instead of `print()`

---

## 👤 Developer

**VISHAL YADAV**
- GitHub: [@VISHAL108-Mech](https://github.com/VISHAL108-Mech)
- LinkedIn: [vishal-yadav-2a91a7428](https://www.linkedin.com/in/vishal-yadav-2a91a7428)
- Email: [vy4122000@gmail.com](mailto:vy4122000@gmail.com)
