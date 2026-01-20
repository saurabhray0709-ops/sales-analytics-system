import requests

def fetch_exchange_rates(base_currency="USD"):
    """
    Fetches live exchange rates from an external API.
   
    """
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status() # Check for HTTP errors
        data = response.json()
        return data.get('rates', {})
    except requests.exceptions.RequestException as e:
        print(f"Error fetching rates: {e}")
        # Fallback rates if API is down
        return {"INR": 83.0, "EUR": 0.92, "GBP": 0.79}

def fetch_region_managers():
    """
    Simulates fetching region manager data from an API.
    """
    # This is often a mock API or a specific URL provided in Masai tasks
    return {
        "North": "Amit Sharma",
        "South": "Priya Mani",
        "East": "Rajesh Gupta",
        "West": "Sneha Patil"
    }