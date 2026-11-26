from database import get_connection


def calculate_impact(price, category_id):

    with get_connection() as connection:

        category = connection.execute("""
            SELECT impact_value
            FROM categories
            WHERE category_id = ? AND is_active = 1
        """, (category_id,)).fetchone()

        if category is None:
            raise ValueError("Category not found.")

        return float(price) * float(category["impact_value"])


def add_purchase(category_id, product_name, price, brand, purchase_date):

    product_name = product_name.strip()

    if not product_name:
        raise ValueError("Enter a product name.")

    if float(price) <= 0:
        raise ValueError("Price must be greater than zero.")

    with get_connection() as connection:

        category = connection.execute("""
            SELECT impact_value
            FROM categories
            WHERE category_id = ? AND is_active = 1
        """, (category_id,)).fetchone()

        if category is None:
            raise ValueError("Please select a valid category.")

        impact = float(price) * float(category["impact_value"])

        cursor = connection.execute("""
            INSERT INTO purchases
            (category_id, product_name, price, brand,
             purchase_date, estimated_impact)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            category_id,
            product_name,
            float(price),
            brand.strip(),
            str(purchase_date),
            impact
        ))

        return cursor.lastrowid, impact


def get_purchase_history():

    with get_connection() as connection:

        return connection.execute("""
            SELECT
                purchases.purchase_id,
                purchases.product_name,
                purchases.price,
                purchases.brand,
                purchases.purchase_date,
                purchases.estimated_impact,
                categories.category_name

            FROM purchases

            JOIN categories
            ON purchases.category_id = categories.category_id

            ORDER BY purchases.purchase_date DESC,
                     purchases.purchase_id DESC
        """).fetchall()


def delete_purchase(purchase_id):

    with get_connection() as connection:

        connection.execute("""
            DELETE FROM purchases
            WHERE purchase_id = ?
        """, (purchase_id,))


def get_monthly_summary(year, month):

    with get_connection() as connection:

        return connection.execute("""
            SELECT
                COUNT(*) AS total_purchases,
                COALESCE(SUM(price), 0) AS total_spending,
                COALESCE(SUM(estimated_impact), 0) AS total_impact

            FROM purchases

            WHERE strftime('%Y', purchase_date) = ?
            AND strftime('%m', purchase_date) = ?
        """, (str(year), f"{int(month):02d}")).fetchone()


def submit_category_request(
    product_name,
    category_name,
    suggested_value=None
):

    if not product_name.strip() or not category_name.strip():
        raise ValueError("Enter the product name and category.")

    if suggested_value is not None:

        suggested_value = float(suggested_value)

        if not 0 <= suggested_value <= 1:
            raise ValueError("Impact value must be between 0 and 1.")

    with get_connection() as connection:

        cursor = connection.execute("""
            INSERT INTO category_requests
            (product_name, category_name, suggested_value)
            VALUES (?, ?, ?)
        """, (
            product_name.strip(),
            category_name.strip(),
            suggested_value
        ))

        return cursor.lastrowid