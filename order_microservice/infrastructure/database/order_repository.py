import psycopg2

from domain.models.order import Order
from domain.models.order_item import OrderItem


class OrderRepository:
    def __init__(self, db_config):
        self.db_config = db_config

    def get_connection(self):
        return psycopg2.connect(**self.db_config)

    def save_order_in_transaction(self, cursor, order: Order):
        insert_order = """
                INSERT INTO order_table (order_id, status, total_price)
                VALUES (%s, %s, %s)
            """
        cursor.execute(
            insert_order,
            (order.order_id, order.status, order.total_price)
        )
        insert_items = """
                INSERT INTO order_item (order_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
            """
        for item in order.order_items:
            cursor.execute(
                insert_items,
                (order.order_id, item.product_id, item.quantity, item.unit_price)
            )

    def find_order_in_transaction(self, cursor, order_id: str) -> Order:
        select_order_sql = """
            SELECT order_id, status, total_price 
            FROM order_table 
            WHERE order_id = %s
        """
        cursor.execute(select_order_sql, (order_id,))
        row = cursor.fetchone()
        if not row:
            return None

        select_items_sql = """
            SELECT product_id, quantity, unit_price
            FROM order_item
            WHERE order_id = %s
        """
        cursor.execute(select_items_sql, (order_id,))
        item_rows = cursor.fetchall()
        order_items = [OrderItem(r[0], r[1], r[2]) for r in item_rows]

        loaded_order = Order(row[0], order_items)
        loaded_order.status = row[1]
        return loaded_order

    def update_order_in_transaction(self, cursor, order: Order):
        update_order_sql = """
            UPDATE order_table 
            SET status = %s, total_price = %s
            WHERE order_id = %s
        """
        cursor.execute(update_order_sql, (order.status, order.total_price, order.order_id))

        delete_items_sql = "DELETE FROM order_item WHERE order_id = %s"
        cursor.execute(delete_items_sql, (order.order_id,))

        insert_item_sql = """
            INSERT INTO order_item (order_id, product_id, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
        """

        for item in order.order_items:
            cursor.execute(
                insert_item_sql,
                (order.order_id, item.product_id, item.quantity, item.unit_price))

    def save_order(self, order: Order):
        connection = psycopg2.connect(**self.db_config)
        try:
            with connection.cursor() as cursor:
                insert_order = """
                    INSERT INTO order_table (order_id, status, total_price)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_order, (order.order_id, order.status, order.total_price))

                insert_item = """
                    INSERT INTO order_item (order_id, product_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                """
                for item in order.order_items:
                    cursor.execute(insert_item, (
                        order.order_id,
                        item.product_id,
                        item.quantity,
                        item.unit_price
                    ))

            connection.commit()
        finally:
            connection.close()

    def find_by_id(self, order_id: str) -> Order:
        connection = psycopg2.connect(**self.db_config)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT order_id, status, total_price FROM t_order WHERE order_id=%s", (order_id,))
                row = cursor.fetchone()
                if not row:
                    return None

                cursor.execute("""
                    SELECT product_id, quantity, unit_price 
                    FROM order_item 
                    WHERE order_id=%s
                """, (order_id,))
                items_rows = cursor.fetchall()
                items = [OrderItem(r[0], r[1], r[2]) for r in items_rows]

                loaded_order = Order(row[0], items)
                loaded_order.status = row[1]
                return loaded_order
        finally:
            connection.close()
