import os
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for


BASE_DIR = Path(__file__).resolve().parent
DB_NAME = os.environ.get("DB_NAME", str(BASE_DIR / "inventory_web.db"))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
            """
        )


@app.route("/")
def index():
    with get_db() as conn:
        products = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
        sales = conn.execute(
            """
            SELECT sales.id, products.name, sales.quantity, sales.date
            FROM sales
            JOIN products ON products.id = sales.product_id
            ORDER BY sales.id DESC
            LIMIT 10
            """
        ).fetchall()

    total_products = len(products)
    total_stock = sum(product["stock"] for product in products)
    low_stock = sum(1 for product in products if product["stock"] <= 5)

    return render_template(
        "index.html",
        products=products,
        sales=sales,
        total_products=total_products,
        total_stock=total_stock,
        low_stock=low_stock,
    )


@app.route("/products", methods=["GET", "POST"])
def add_product():
    if request.method == "GET":
        return redirect(url_for("index"))

    name = request.form.get("name", "").strip()
    price = request.form.get("price", "").strip()
    stock = request.form.get("stock", "").strip()

    if not name:
        flash("Product name is required.", "error")
        return redirect(url_for("index"))

    try:
        price_value = float(price)
        stock_value = int(stock)
        if price_value < 0 or stock_value < 0:
            raise ValueError
    except ValueError:
        flash("Price and stock must be valid positive numbers.", "error")
        return redirect(url_for("index"))

    with get_db() as conn:
        conn.execute(
            "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
            (name, price_value, stock_value),
        )

    flash("Product added successfully.", "success")
    return redirect(url_for("index"))


@app.post("/products/<int:product_id>/delete")
def delete_product(product_id):
    with get_db() as conn:
        conn.execute("DELETE FROM sales WHERE product_id = ?", (product_id,))
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))

    flash("Product deleted successfully.", "success")
    return redirect(url_for("index"))


@app.route("/sales", methods=["GET", "POST"])
def record_sale():
    if request.method == "GET":
        return redirect(url_for("index"))

    product_id = request.form.get("product_id", "").strip()
    quantity = request.form.get("quantity", "").strip()

    try:
        product_id_value = int(product_id)
        quantity_value = int(quantity)
        if quantity_value <= 0:
            raise ValueError
    except ValueError:
        flash("Please choose a product and enter a valid quantity.", "error")
        return redirect(url_for("index"))

    with get_db() as conn:
        product = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id_value,)
        ).fetchone()

        if product is None:
            flash("Selected product was not found.", "error")
            return redirect(url_for("index"))

        if quantity_value > product["stock"]:
            flash("Not enough stock for this sale.", "error")
            return redirect(url_for("index"))

        conn.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (quantity_value, product_id_value),
        )
        conn.execute(
            "INSERT INTO sales (product_id, quantity, date) VALUES (?, ?, ?)",
            (
                product_id_value,
                quantity_value,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )

    flash("Sale recorded successfully.", "success")
    return redirect(url_for("index"))


init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
