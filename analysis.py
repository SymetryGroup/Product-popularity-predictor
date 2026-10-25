import requests
from getpass import getpass
import json


# Wprowadź dane bez zapisywania ich w kodzie
client_id = getpass("Client ID: ")
client_secret = getpass("Client Secret: ")

# Poproś Allegro o token dostępowy
response = requests.post(
    "https://allegro.pl/auth/oauth/token",
    auth=(client_id, client_secret),
    data={"grant_type": "client_credentials"},
    timeout=30
)

print("Kod odpowiedzi:", response.status_code)

response.raise_for_status()
token = response.json()["access_token"]

print("Token uzyskany poprawnie!")

# User-Agent musi odpowiadać wartości skonfigurowanej w portalu
user_agent = "ProductPopularityML/1.0 (+https://developer.allegro.pl/)"

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.allegro.public.v1+json",
    "User-Agent": user_agent
}

url = "https://api.allegro.pl/sale/categories"

response = requests.get(
    url,
    headers=headers,
    timeout=30
)

print("Kod odpowiedzi:", response.status_code)
response.raise_for_status()

data = response.json()

print("Liczba kategorii:", len(data.get("categories", [])))
print(data.get("categories", [])[:3])

print(json.dumps(data, indent=2, ensure_ascii=False))