import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("shopimpact.db")


DEFAULT_CATEGORIES = [
    ("Clothing and textiles", 0.05,
     "Second-hand clothing"),

    ("Second-hand clothing", 0.015,
     "Reuse existing clothing"),

    ("Footwear", 0.06,
     "Repair or buy second-hand footwear"),

    ("Leather footwear", 0.08,
     "Second-hand or non-leather footwear"),

    ("Electronics", 0.12,
     "Repair or buy refurbished electronics"),

    ("Food and groceries", 0.025,
     "Local and seasonal products"),

    ("Packaged food", 0.03,
     "Products with less packaging"),

    ("Personal care", 0.03,
     "Refillable products"),

    ("Household products", 0.035,
     "Reusable products"),

    ("Furniture", 0.07,
     "Second-hand furniture"),

    ("Books and stationery", 0.02,
     "Borrowed or recycled products"),

    ("Transport-related purchases", 0.09,
     "Shared or lower-impact transport"),

    ("Other products", 0.05,
     "Reuse or repair products")
]


def get_connection():

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():

    with get_connection() as connection:

        connection.executescript("""

        CREATE TABLE IF NOT EXISTS categories (

            category_id INTEGER PRIMARY KEY AUTOINCREMENT,

            category_name TEXT NOT NULL UNIQUE,

            impact_value REAL NOT NULL
            CHECK (impact_value >= 0 AND impact_value <= 1),

            greener_alternative TEXT,

            is_active INTEGER DEFAULT 1,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP

        );


        CREATE TABLE IF NOT EXISTS purchases (

            purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,

            category_id INTEGER NOT NULL,

            product_name TEXT NOT NULL,

            price REAL NOT NULL CHECK (price > 0),

            brand TEXT,

            purchase_date TEXT NOT NULL,

            estimated_impact REAL NOT NULL,

            FOREIGN KEY (category_id)
            REFERENCES categories(category_id)

        );


        CREATE TABLE IF NOT EXISTS category_requests (

            request_id INTEGER PRIMARY KEY AUTOINCREMENT,

            product_name TEXT NOT NULL,

            category_name TEXT NOT NULL,

            suggested_value REAL
            CHECK (
                suggested_value IS NULL
                OR (suggested_value >= 0 AND suggested_value <= 1)
            ),

            request_status TEXT DEFAULT 'Pending',

            admin_note TEXT,

            request_date TEXT DEFAULT CURRENT_TIMESTAMP

        );

        """)

        existing = connection.execute(
            "SELECT COUNT(*) FROM categories"
        ).fetchone()[0]

        if existing == 0:

            connection.executemany("""

                INSERT INTO categories
                (category_name, impact_value, greener_alternative)

                VALUES (?, ?, ?)

            """, DEFAULT_CATEGORIES)


def get_categories():

    with get_connection() as connection:

        return connection.execute("""

            SELECT *
            FROM categories
            WHERE is_active = 1
            ORDER BY category_name

        """).fetchall()


if __name__ == "__main__":

    initialize_database()

    print("ShopImpact database created successfully.")

    print("Available categories:", len(get_categories()))