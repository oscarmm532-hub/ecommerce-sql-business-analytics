import os
import random
import sqlite3
from datetime import datetime, timedelta


def build_ecommerce_db(db_path="data/ecommerce.db"):
  os.makedirs(os.path.dirname(db_path), exist_ok=True)
  if os.path.exists(db_path):
    os.remove(db_path)

  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()
  cursor.execute("PRAGMA foreign_keys = ON;")

  # 1. Creación de tablas normalizadas (Esquema Estrella)
  cursor.executescript("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        full_name TEXT NOT NULL,
        country TEXT NOT NULL,
        segment TEXT NOT NULL,
        signup_date TEXT NOT NULL
    );

    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        unit_price REAL NOT NULL
    );

    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)

  random.seed(42)

  # 2. Poblar catálogo de productos
  products = [
      (1, "Wireless Noise-Canceling Headphones", "Electronics", 180.00),
      (2, "4K USB-C Docking Station", "Electronics", 120.00),
      (3, "Mechanical Keyboard RGB", "Electronics", 95.00),
      (4, "Ergonomic Office Chair", "Furniture", 310.00),
      (5, "Standing Desk Converter", "Furniture", 220.00),
      (6, "LED Desk Lamp", "Furniture", 45.00),
      (7, "Insulated Stainless Bottle", "Lifestyle", 28.00),
      (8, "Laptop Backpack Water-Resistant", "Lifestyle", 65.00),
  ]
  cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?);", products)

  # 3. Poblar clientes
  countries = ["Ecuador", "Colombia", "Peru", "Chile", "Mexico"]
  segments = ["Consumer", "Corporate", "Small Business"]
  customers = []
  base_signup = datetime(2025, 6, 1)

  for cid in range(1, 151):
    signup = base_signup + timedelta(days=random.randint(0, 180))
    customers.append((
        cid,
        f"Customer_{cid:03d}",
        random.choice(countries),
        random.choices(segments, weights=[0.55, 0.25, 0.20])[0],
        signup.strftime("%Y-%m-%d"),
    ))
  cursor.executemany(
      "INSERT INTO customers VALUES (?, ?, ?, ?, ?);", customers
  )

  # 4. Poblar 1,200 órdenes históricas entre enero y octubre de 2026
  orders = []
  start_date = datetime(2026, 1, 1)
  statuses = ["Completed", "Completed", "Completed", "Returned", "Cancelled"]

  for oid in range(1, 1201):
    order_dt = start_date + timedelta(days=random.randint(0, 300))
    orders.append((
        oid,
        random.randint(1, 150),
        random.randint(1, 8),
        random.randint(1, 4),
        order_dt.strftime("%Y-%m-%d"),
        random.choice(statuses),
    ))
  cursor.executemany(
      "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?);", orders
  )

  conn.commit()
  conn.close()
  print(f"Relational database built successfully at: {db_path}")


if __name__ == "__main__":
  build_ecommerce_db()
