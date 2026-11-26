from database import get_connection


# 1. GET ALL PENDING CATEGORY REQUESTS

def get_pending_requests():

    with get_connection() as connection:

        requests = connection.execute("""
            SELECT *
            FROM category_requests
            WHERE request_status = 'Pending'
            ORDER BY request_date DESC
        """).fetchall()

        return requests


# 2. ADD A NEW CATEGORY

def add_category(category_name, impact_value, greener_alternative):

    category_name = category_name.strip()
    impact_value = float(impact_value)

    if not category_name:
        raise ValueError("Category name is required.")

    if not 0 <= impact_value <= 1:
        raise ValueError("Impact value must be between 0 and 1.")

    with get_connection() as connection:

        existing = connection.execute("""
            SELECT category_id
            FROM categories
            WHERE category_name = ?
        """, (category_name,)).fetchone()

        if existing:
            raise ValueError("This category already exists.")

        connection.execute("""
            INSERT INTO categories (
                category_name,
                impact_value,
                greener_alternative
            )
            VALUES (?, ?, ?)
        """, (
            category_name,
            impact_value,
            greener_alternative.strip()
        ))


# 3. EDIT AN EXISTING CATEGORY

def edit_category(category_id, impact_value, greener_alternative):

    impact_value = float(impact_value)

    if not 0 <= impact_value <= 1:
        raise ValueError("Impact value must be between 0 and 1.")

    with get_connection() as connection:

        connection.execute("""
            UPDATE categories
            SET impact_value = ?,
                greener_alternative = ?
            WHERE category_id = ?
        """, (
            impact_value,
            greener_alternative.strip(),
            category_id
        ))


# 4. APPROVE A CATEGORY REQUEST

def approve_request(request_id, impact_value=None):

    with get_connection() as connection:

        request = connection.execute("""
            SELECT *
            FROM category_requests
            WHERE request_id = ?
            AND request_status = 'Pending'
        """, (request_id,)).fetchone()

        if request is None:
            raise ValueError("Request not found or already processed.")

        if impact_value is None:
            impact_value = request["suggested_value"]

        if impact_value is None:
            raise ValueError(
                "The administrator must enter an impact value."
            )

        impact_value = float(impact_value)

        if not 0 <= impact_value <= 1:
            raise ValueError("Impact value must be between 0 and 1.")

        category_name = request["category_name"]

        existing = connection.execute("""
            SELECT category_id
            FROM categories
            WHERE category_name = ?
        """, (category_name,)).fetchone()

        if existing:

            connection.execute("""
                UPDATE categories
                SET impact_value = ?,
                    is_active = 1
                WHERE category_id = ?
            """, (
                impact_value,
                existing["category_id"]
            ))

        else:

            connection.execute("""
                INSERT INTO categories (
                    category_name,
                    impact_value,
                    greener_alternative
                )
                VALUES (?, ?, ?)
            """, (
                category_name,
                impact_value,
                "Consider reusable or second-hand alternatives"
            ))

        connection.execute("""
            UPDATE category_requests
            SET request_status = 'Approved'
            WHERE request_id = ?
        """, (request_id,))


# 5. REJECT A CATEGORY REQUEST

def reject_request(request_id, admin_note=""):

    with get_connection() as connection:

        connection.execute("""
            UPDATE category_requests
            SET request_status = 'Rejected',
                admin_note = ?
            WHERE request_id = ?
            AND request_status = 'Pending'
        """, (
            admin_note,
            request_id
        ))


# 6. GET ALL CATEGORIES

def get_all_categories():

    with get_connection() as connection:

        categories = connection.execute("""
            SELECT *
            FROM categories
            ORDER BY category_name
        """).fetchall()

        return categories


# 7. ACTIVATE OR DEACTIVATE A CATEGORY

def set_category_active(category_id, is_active):

    is_active = int(is_active)

    if is_active not in (0, 1):
        raise ValueError("Status must be 0 or 1.")

    with get_connection() as connection:

        connection.execute("""
            UPDATE categories
            SET is_active = ?
            WHERE category_id = ?
        """, (
            is_active,
            category_id
        ))