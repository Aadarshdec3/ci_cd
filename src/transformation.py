import pandas as pd
import os
import sqlite3

def transform_sales(fact, products):

    # 1. Clean required fields only (not full dropna)
    fact = fact.dropna(subset=["ProductID", "SalesDate", "Quantity"])

    # 2. Safe date conversion
    fact["SalesDate"] = pd.to_datetime(fact["SalesDate"], errors="coerce")
    fact = fact.dropna(subset=["SalesDate"])
    fact["SalesDate"] = fact["SalesDate"].dt.floor("D")

    # 3. Merge product data
    fact = pd.merge(
        fact,
        products[["ProductID", "Price"]],
        on="ProductID",
        how="left"
    )

    # 4. Handle missing prices
    fact["Price"] = fact["Price"].fillna(0)

    # 5. Ensure numeric safety
    fact["Quantity"] = pd.to_numeric(fact["Quantity"], errors="coerce").fillna(0)
    fact["Discount"] = pd.to_numeric(fact["Discount"], errors="coerce").fillna(0)

    # 6. Business logic
    fact["TotalPrice"] = fact["Quantity"] * fact["Price"]
    fact["TotalPrice"] = fact["TotalPrice"] - (
        fact["TotalPrice"] * (fact["Discount"] / 100)
    )

    # 7. Time dimension
    fact["month"] = fact["SalesDate"].dt.to_period("M")

    # 8. Aggregation (Gold layer)
    fact = fact.groupby(
        ["SalesPersonID", "ProductID", "month"]
    ).agg(
        total_qty=("Quantity", "sum"),
        total_price=("TotalPrice", "sum")
    ).reset_index()

    return fact

env = os.getenv("env","dev")

fact_path = f"../data/{env}/sales.csv"
products_path = f"../data/{env}/products.csv"

fact = pd.read_csv(fact_path)
products = pd.read_csv(products_path)

gold = transform_sales(fact, products)

# ensure db folder exists
os.makedirs("db", exist_ok=True)

#load to sqlite
db_name = f"db/{env}_etl.db"

conn=sqlite3.connect(db_name)

gold.to_sql(
    "fact_gold",
    conn,
    if_exists="replace",
    index=False
)

conn.close()