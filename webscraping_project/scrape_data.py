import requests
import sqlite3
from bs4 import BeautifulSoup

conn = sqlite3.connect("products.db")
cursor = conn.cursor()

# DO NOT change schema
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    brand TEXT,
    price REAL,
    original_price REAL,
    category TEXT,
    subcategory TEXT,
    image TEXT,
    description TEXT
)
""")

def insert_product(p):
    cursor.execute("""
        INSERT INTO products
        (title, brand, price, original_price, category, subcategory, image, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, p)

# ---------------- API SCRAPING ----------------
dummy_url = "https://dummyjson.com/products?limit=100"
dummy_products = requests.get(dummy_url).json()["products"]

# Expanded banned keywords to remove all grocery/food/fresh items
banned = [
    "water", "juice", " Fish Steak", "vegetable", "fruit", "oil", "Beef Steak", "food", "snacks",
    "mulberry", "potatoes", "milk", "onion", "strawberry", "kiwi", "apple", "banana", "tomato"
]

for item in dummy_products:
    if any(b in item["title"].lower() for b in banned):
        continue

    price = item["price"] * 83

    insert_product((
        item["title"],
        item.get("brand", "Generic"),
        round(price, 2),
        round(price * 1.2, 2),
        item["category"],
        item["category"],
        item["thumbnail"],
        item["description"]
    ))

# ---------------- HTML SCRAPING (Books only) ----------------
books_url = "https://books.toscrape.com/"
response = requests.get(books_url)
response.encoding = "utf-8"

soup = BeautifulSoup(response.text, "html.parser")
books = soup.select(".product_pod")[:20]

for book in books:
    title = book.h3.a["title"]

    price_text = book.select_one(".price_color").text
    price_text = price_text.replace("£", "").replace("Â", "")
    price = float(price_text) * 105

    image = books_url + book.img["src"].replace("../", "")

    insert_product((
        title,
        "Unknown",
        round(price, 2),
        round(price * 1.3, 2),
        "Books",          # Only new category
        "Books",
        image,
        "A quality book useful for learning, imagination, and personal growth."
    ))

conn.commit()
conn.close()

print("✔ API data + Books added successfully")