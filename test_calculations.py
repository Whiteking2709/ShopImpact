from database import get_categories, get_connection
from calculations import (
    calculate_impact,
    add_purchase,
    get_purchase_history,
    delete_purchase,
    get_monthly_summary,
    submit_category_request
)

from datetime import date


print("\nSHOPIMPACT TESTING")
print("--------------------------")

# Test 1: Retrieve categories
categories = get_categories()

print("Test 1: Retrieve categories:", len(categories), "categories found")

# Test 2: Calculate impact
category = next(
    item for item in categories
    if item["category_name"] == "Clothing and textiles"
)

impact = calculate_impact(2000, category["category_id"])

print("Test 2: Calculate impact:", impact, "points")

# Test 3: Add purchase
purchase_id, saved_impact = add_purchase(
    category["category_id"],
    "Test T-shirt",
    2000,
    "Test Brand",
    date.today()
)

print("Test 3: Add purchase: Successful")

# Test 4: Retrieve purchase history
history = get_purchase_history()

print("Test 4: Purchase history:", len(history), "records found")

# Test 5: Monthly summary
today = date.today()

summary = get_monthly_summary(
    today.year,
    today.month
)

print("Test 5: Monthly spending:", summary["total_spending"])

# Test 6: Submit category request
request_id = submit_category_request(
    "Test Product",
    "Test Category",
    0.4
)

print("Test 6: Category request: Successful")

# Clean up test records
delete_purchase(purchase_id)

with get_connection() as connection:
    connection.execute(
        "DELETE FROM category_requests WHERE request_id = ?",
        (request_id,)
    )

print("\nAll tests completed.")
print("Temporary test records deleted.")