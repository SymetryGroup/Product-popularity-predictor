
import base64
import hashlib
import secrets
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, urlparse, parse_qs
from getpass import getpass

import requests

CLIENT_ID = input("Podaj Client ID: ").strip()
REDIRECT_URI = "http://localhost:8080/callback"

AUTH_URL = "https://allegro.pl/auth/oauth/authorize"
TOKEN_URL = "https://allegro.pl/auth/oauth/token"

# Zabezpieczenia procesu logowania (PKCE)
verifier = secrets.token_urlsafe(64)
challenge = base64.urlsafe_b64encode(
    hashlib.sha256(verifier.encode("ascii")).digest()
).rstrip(b"=").decode("ascii")

state = secrets.token_urlsafe(24)
auth_result = {}

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)

        if query.get("state", [""])[0] != state:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid state. Close this page.")
            return

        auth_result["code"] = query.get("code", [None])[0]
        auth_result["error"] = query.get("error", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        message = (
            "Logowanie zakonczone. Wroc do VS Code."
            if auth_result["code"]
            else "Autoryzacja nie powiodla sie. Wroc do VS Code."
        )
        self.wfile.write(message.encode("utf-8"))

    def log_message(self, format, *args):
        pass

server = HTTPServer(("localhost", 8080), CallbackHandler)
server.timeout = 180

params = {
    "response_type": "code",
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "code_challenge_method": "S256",
    "code_challenge": challenge,
    "state": state,
}

login_url = AUTH_URL + "?" + urlencode(params)

print("Otwieram stronę logowania Allegro...")
threading.Thread(target=webbrowser.open, args=(login_url,), daemon=True).start()

try:
    server.handle_request()
finally:
    server.server_close()

if not auth_result.get("code"):
    raise SystemExit(
        f"Logowanie nie powiodło się: {auth_result.get('error')}"
    )

# Wymiana jednorazowego kodu na token
token_response = requests.post(
    TOKEN_URL,
    data={
        "grant_type": "authorization_code",
        "code": auth_result["code"],
        "redirect_uri": REDIRECT_URI,
        "code_verifier": verifier,
        "client_id": CLIENT_ID,
    },
    timeout=30,
)

print("Status tokena:", token_response.status_code)

if token_response.status_code != 200:
    print(token_response.text[:1000])
    raise SystemExit("Nie udało się uzyskać tokena.")

tokens = token_response.json()
token = tokens["access_token"]

print("Token użytkownika uzyskany poprawnie!")
print("Nie udostępniaj tokenu innym osobom.")

response = requests.get(
    "https://api.allegro.pl/sale/products",
    headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    },
    params={
        "phrase": "słuchawki",
        "language": "pl-PL"
    },
    timeout=30
)

print("Status produktów:", response.status_code)
print(response.text[:1500])

response = requests.get(
    "https://api.allegro.pl/sale/products",
    headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    },
    params={
        "phrase": "słuchawki",
        "language": "pl-PL"
    },
    timeout=30
)

print("Status:", response.status_code)

if response.status_code == 200:
    data_products = response.json()
    print("Klucze:", data_products.keys())
    print("Dane:", str(data_products)[:2000])
else:
    print(response.text[:1000])


import pandas as pd
import json

# Sprawdź strukturę odpowiedzi
print("Klucze odpowiedzi:", data_products.keys())

# Pobierz listę produktów
products = data_products.get("products", [])

rows = []

for product in products:
    category = product.get("category") or {}

    rows.append({
        "id_produktu": product.get("id"),
        "nazwa": product.get("name"),
        "id_kategorii": category.get("id") if isinstance(category, dict) else None,
        "parametry": json.dumps(
            product.get("parameters", []),
            ensure_ascii=False
        )
    })

df = pd.DataFrame(
    rows,
    columns=["id_produktu", "nazwa", "id_kategorii", "parametry"]
)

df.to_csv(
    "produkty_allegro.csv",
    index=False,
    encoding="utf-8-sig"
)

print(df.head(10))
print(f"Zapisano {len(df)} produktów do produkty_allegro.csv")



import pandas as pd
import json

# Wczytaj zapisany plik CSV
df = pd.read_csv("produkty_allegro.csv")

# Pokaż podstawowe informacje
print("Liczba produktów:", len(df))
print("\nKolumny:")
print(df.columns.tolist())

print("\nBrakujące wartości:")
print(df.isna().sum())

# Rozpakuj parametry produktów do osobnych kolumn
parameters = []

for raw in df["parametry"]:
    try:
        params = json.loads(raw) if isinstance(raw, str) else []
    except json.JSONDecodeError:
        params = []

    row = {}
    for param in params:
        name = param.get("name")
        values = param.get("valuesLabels", [])
        row[name] = ", ".join(values) if values else None

    parameters.append(row)

params_df = pd.DataFrame(parameters)
df_clean = pd.concat(
    [df.drop(columns=["parametry"]), params_df],
    axis=1
)

df_clean.to_csv(
    "produkty_allegro_analiza.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nZapisano produkty_allegro_analiza.csv")
print(df_clean.head())



import requests

product_id = "415a77d9-b909-4109-bb6c-0960de236912"

response = requests.get(
    f"https://api.allegro.pl/sale/products/{product_id}",
    headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    },
    timeout=30
)

print("Status:", response.status_code)
print(response.text[:3000])

product_data = response.json()

print("Klucze odpowiedzi:")
print(product_data.keys())

print("\nPełna odpowiedź:")
print(response.text[:4000])

import time

# Wczytaj wcześniej zapisane produkty
products_df = pd.read_csv("produkty_allegro.csv")

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.allegro.public.v1+json"
}

rows = []

for _, row in products_df.iterrows():
    product_id = row["id_produktu"]

    url = f"https://api.allegro.pl/sale/products/{product_id}"

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            print(f"Błąd dla {product_id}: {response.status_code}")
            continue

        product = response.json()
        category = product.get("category", {})

        # Zapisz podstawowe dane
        item = {
            "id_produktu": product.get("id"),
            "nazwa": product.get("name"),
            "id_kategorii": category.get("id"),
            "sciezka_kategorii": " > ".join(
                c.get("name", "")
                for c in category.get("path", [])
            )
        }

        # Rozdziel parametry produktu na kolumny
        for param in product.get("parameters", []):
            name = param.get("name", "nieznany_parametr")
            values = param.get("valuesLabels") or param.get("values") or []
            item[name] = ", ".join(map(str, values))

        rows.append(item)
        print("Pobrano:", product.get("name"))

        time.sleep(0.2)

    except requests.RequestException as e:
        print(f"Błąd połączenia dla {product_id}: {e}")

# Utwórz tabelę i wyeksportuj dane
df_details = pd.DataFrame(rows)

df_details.to_csv(
    "produkty_allegro_szczegoly.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nLiczba pobranych produktów:", len(df_details))
print("Plik: produkty_allegro_szczegoly.csv")
print(df_details.head())