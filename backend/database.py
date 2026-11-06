import sqlite3

DATABASE_NAME = "customer_support.db"


def create_database():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            product TEXT NOT NULL,
            status TEXT NOT NULL,
            tracking_number TEXT,
            expected_delivery TEXT
        )
    """)

    connection.commit()

    connection.close()


def insert_sample_orders():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    orders = [
        (1001, "Talal", "Laptop", "Shipped", "DHL-1001-DE", "2026-11-08"),
        (1002, "Anna", "Headphones", "Processing", None, "2026-11-10"),
        (1003, "John", "Keyboard", "Delivered", "DHL-1003-DE", "2026-11-03"),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO orders (
            order_id,
            customer_name,
            product,
            status,
            tracking_number,
            expected_delivery
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        orders,
    )
    # VALUES (?, ?, ?, ?, ?, ?) it would be replaced with orders values

    connection.commit()

    connection.close()


def get_order(order_id: int):

    connection = sqlite3.connect(DATABASE_NAME)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM orders
        WHERE order_id = ?
        """,
        (order_id,),
    )

    order = cursor.fetchone()

    connection.close()

    if order is None:
        return None

    return dict(order)


if __name__ == "__main__":
    create_database()
    insert_sample_orders()

    # print("Database initialized successfully.")
    order = get_order(1002)
    print(order)
