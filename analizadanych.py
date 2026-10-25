import pandas as pd
import matplotlib.pyplot as plt 

df = pd.read_csv("produkty_allegro_szczegoly.csv")

print("Liczba produktów :" , len(df))
print("Liczba kolumn :" , len(df.columns))

print("\nInformacje o kolumnach:")
df.info()


# 2. Brakujące wartości
braki = df.isnull().sum().sort_values(ascending=False)

print("\nKolumny z największą liczbą braków:")
print(braki.head(15))

# 3. Liczba unikalnych produktów
print("\nLiczba unikalnych ID:")
print(df["id_produktu"].nunique())

# 4. Najczęstsze kategorie
print("\nNajczęstsze kategorie:")
print(df["sciezka_kategorii"].value_counts().head(10))


# 5. Wykres z krótkimi nazwami kategorii

liczba_kategorii = df["sciezka_kategorii"].value_counts().head(10)

# Zostawiamy tylko ostatnią część ścieżki kategorii
krotkie_nazwy = liczba_kategorii.index.to_series().apply(
    lambda x: x.split(" > ")[-1]
)

# Łączymy nazwy z liczbą produktów
wykres = pd.Series(
    liczba_kategorii.values,
    index=krotkie_nazwy.values
)

plt.figure(figsize=(12, 6))
wykres.plot(kind="bar")

plt.title("Liczba produktów według kategorii")
plt.xlabel("Kategoria")
plt.ylabel("Liczba produktów")
plt.xticks(rotation=35, ha="right")

plt.tight_layout()
plt.savefig(
    "liczba_produktow_kategorie.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()
