from admin import (
    get_pending_requests,
    add_category,
    edit_category,
    approve_request,
    reject_request,
    get_all_categories
)

from calculations import submit_category_request
from database import get_connection


print("\nSHOPIMPACT ADMIN TESTING")
print("--------------------------")

# Create a temporary category request
request_id = submit_category_request(
    "Test product",
    "Test admin category",
    0.4
)

print("Test 1: Category request created")

# Retrieve pending requests
requests = get_pending_requests()

print("Test 2: Pending requests:", len(requests))

# Approve request
approve_request(request_id)

print("Test 3: Approve request successful")

# Edit category
with get_connection() as connection:
    category = connection.execute("""
        SELECT category_id
        FROM categories
        WHERE category_name = 'Test admin category'
    """).fetchone()

edit_category(
    category["category_id"],
    0.5,
    "Test greener alternative"
)

print("Test 4: Edit category successful")

# Reject another request
second_request = submit_category_request(
    "Another test product",
    "Another test category"
)

reject_request(second_request, "Test rejection")

print("Test 5: Reject request successful")

# Remove temporary test records
with get_connection() as connection:
    connection.execute("""
        DELETE FROM categories
        WHERE category_name = 'Test admin category'
    """)

    connection.execute("""
        DELETE FROM category_requests
        WHERE request_id = ?
    """, (second_request,))

print("\nAll administrator tests completed.")
print("Temporary records removed.")