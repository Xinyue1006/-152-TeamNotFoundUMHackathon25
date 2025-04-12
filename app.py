import pandas as pd

# Load data
df_orders = pd.read_csv("transaction_data.csv")
df_items = pd.read_csv("items.csv")
df_transaction_items = pd.read_csv("transaction_items.csv")
df_merchants = pd.read_csv("merchant.csv")  # Contains merchant_id + merchant_name

# SELECT merchant here
merchant_id = "3e2b6"  # You can change this ID to test others like "2b5d7", etc.

# Get merchant name for output
merchant_name = df_merchants[df_merchants["merchant_id"] == merchant_id]["merchant_name"].values[0]

# Filter order data for selected merchant
df_bagel = df_orders[df_orders["merchant_id"] == merchant_id].copy()

# Fix datetime format safely
df_bagel["order_time"] = pd.to_datetime(df_bagel["order_time"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
df_bagel = df_bagel.dropna(subset=["order_time"])

# Extract week and year
df_bagel["week"] = df_bagel["order_time"].dt.isocalendar().week
df_bagel["year"] = df_bagel["order_time"].dt.isocalendar().year

# Get latest week and year
latest_year = df_bagel["year"].max()
latest_week = df_bagel[df_bagel["year"] == latest_year]["week"].max()

# This week's and last week's data
this_week = df_bagel[(df_bagel["week"] == latest_week) & (df_bagel["year"] == latest_year)]
last_week = df_bagel[(df_bagel["week"] == (latest_week - 1)) & (df_bagel["year"] == latest_year)]

# Revenue
this_week_sales = this_week["order_value"].sum()
last_week_sales = last_week["order_value"].sum()
sales_change = ((this_week_sales - last_week_sales) / last_week_sales * 100) if last_week_sales > 0 else 0

# Sales trend response
print("MEXA: Let's take a look at your weekly sales performance.")
print(f"MEXA: This week's sales for {merchant_name}: ${this_week_sales:.2f}")
print(f"MEXA: Last week's sales for {merchant_name}: ${last_week_sales:.2f}")
print(f"MEXA: Sales change: {sales_change:.2f}% —", end=" ")

if sales_change > 15:
    print("great job! Sales are up this week.")
elif sales_change < -15:
    print("sales dropped significantly — consider revisiting promotions.")
else:
    print("your sales are stable this week.")

# Simulate mock quantities for transaction items
df_transaction_items["quantity"] = 1

# Filter only this merchant's items
df_items_merchant = df_items[df_items["merchant_id"] == merchant_id]

# Merge transaction items with items (filtered to this merchant)
transaction_items_merged = pd.merge(
    df_transaction_items, 
    df_items_merchant[["item_id", "item_name", "merchant_id"]], 
    on="item_id"
)

# Get only this week's orders for this merchant
this_week_order_ids = this_week["order_id"].unique()
this_week_items = transaction_items_merged[transaction_items_merged["order_id"].isin(this_week_order_ids)]

# Top-selling product this week
top_selling = this_week_items.groupby("item_name")["quantity"].sum().reset_index(name="sold")
if not top_selling.empty:
    best_seller = top_selling.sort_values(by="sold", ascending=False).iloc[0]
    print(f"MEXA: Top-selling item this week: {best_seller['item_name']} (sold {best_seller['sold']} units)")
else:
    print("MEXA: No top-selling item data available this week.")

print("MEXA: A visual dashboard has been sent to the frontend.")

# Inventory check
print("\nMEXA: Checking your inventory...")

# Total items sold (assumed to simulate remaining stock)
sold_per_item = transaction_items_merged.groupby("item_name")["quantity"].sum().reset_index(name="sold")
sold_per_item["remaining_stock"] = sold_per_item["sold"].apply(lambda x: max(0, 100 - x))  # cap at 0

# Identify low stock (threshold < 10 units)
low_stock = sold_per_item[sold_per_item["remaining_stock"] < 10]

# Show only one low stock alert
if not low_stock.empty:
    first_low = low_stock.iloc[0]
    print(f"MEXA: Low stock for {first_low['item_name']} (only ~{first_low['remaining_stock']} left)")
else:
    print("MEXA: Inventory levels are sufficient.")

# Recommendation AI
print("\nMEXA: Personalized Tip:")
print("MEXA: Add photos or better descriptions to attract more orders.")
