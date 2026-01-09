from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
DB_NAME = "products.db"

# Add banned categories here
BANNED_CATEGORIES = ['grocery', 'food', 'fruits', 'vegetables', 'water', 'juice', 'meat', 'oil']

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    # Table for recent searches
    cur.execute("""
    CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def get_categories():
    conn = get_db()
    cur = conn.cursor()
    # Exclude banned categories dynamically
    placeholders = ",".join(["?"] * len(BANNED_CATEGORIES))
    query = f"""
        SELECT DISTINCT category 
        FROM products 
        WHERE category NOT IN ({placeholders})
        ORDER BY category
    """
    cur.execute(query, BANNED_CATEGORIES)
    data = [row["category"] for row in cur.fetchall()]
    conn.close()
    return data

def get_search_history():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT keyword FROM searches ORDER BY id DESC LIMIT 10")
    history = [row["keyword"] for row in cur.fetchall()]
    conn.close()
    return history

@app.route("/")
def index():
    q = request.args.get("q", "")
    category = request.args.get("category", "")

    conn = get_db()
    cur = conn.cursor()

    # Exclude banned categories dynamically in product listing
    placeholders = ",".join(["?"] * len(BANNED_CATEGORIES))
    query = f"SELECT * FROM products WHERE category NOT IN ({placeholders})"
    params = BANNED_CATEGORIES.copy()

    if q:
        query += " AND title LIKE ?"
        params.append(f"%{q}%")
        cur.execute("INSERT INTO searches (keyword) VALUES (?)", (q,))

    if category:
        query += " AND category = ?"
        params.append(category)

    cur.execute(query, params)
    products = cur.fetchall()
    conn.commit()
    conn.close()

    return render_template(
        "index.html",
        products=products,
        categories=get_categories(),
        history=get_search_history()
    )

@app.route("/product/<int:pid>")
def product_detail(pid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE id=?", (pid,))
    product = cur.fetchone()
    conn.close()
    return render_template("product.html", product=product)

if __name__ == "__main__":
    app.run(debug=True)
