from flask import current_app as app
from datetime import date

import pandas as pd


class Inventory:
    """
    this is the class for pulling rows from the inventory table
    """

    def __init__(self, sid, pid, price_per_item, quantity, modified_date, promo_code):
        self.sid = sid
        self.pid = pid
        self.price_per_item = price_per_item
        self.quantity = quantity
        self.modified_date = modified_date
        self.promo_code = promo_code
        self.start = 0
        self.end = 5
        self.columns = [
            "sid",
            "pid",
            "price_per_item",
            "quantity",
            "modified_date",
            "promo_code",
        ]

    @staticmethod
    def get_user_inventory(sid, return_colnames=False):
        rows = app.db.execute(
            """
            SELECT Inventory.sid, Products.id, Products.name, Inventory.price, Inventory.promo_code, Inventory.quantity
            FROM Inventory
            INNER JOIN Products ON Inventory.pid = Products.id
            WHERE Inventory.quantity > 0
            AND Inventory.sid = :sid
            ORDER BY Products.id;
            """,
            sid=sid,
        )
        colnames = ["sid", "pid", "name", "price", "promo_code", "quantity"]
        if return_colnames:
            return rows, colnames
        else:
            return rows, Inventory(*rows[0]) if len(rows) > 0 else None

    @staticmethod
    def get_user_product(sid, pid, return_colnames=False):
        rows = app.db.execute(
            """
            SELECT Inventory.sid, Products.id, Products.name, Inventory.price, Inventory.promo_code, Inventory.quantity
            FROM Inventory
            INNER JOIN Products ON Inventory.pid = Products.id
            AND Inventory.sid = :sid
            AND Products.id = :pid
            """,
            sid=sid,
            pid=pid,
        )
        colnames = ["sid", "pid", "name", "price", "promo_code", "quantity"]
        if return_colnames:
            return rows, colnames
        else:
            return rows

    @staticmethod
    def get_user_unique_product(sid, pid, promo_code, return_colnames=False):
        rows = app.db.execute(
            """
            SELECT Inventory.sid, Products.id, Products.name, Inventory.price, Inventory.promo_code, Inventory.quantity
            FROM Inventory
            INNER JOIN Products ON Inventory.pid = Products.id
            WHERE Inventory.quantity > 0
            AND Inventory.sid = :sid
            AND Products.id = :pid
            AND Inventory.promo_code = :promo_code
            """,
            sid=sid,
            pid=pid,
            promo_code=promo_code,
        )
        colnames = ["sid", "pid", "name", "price", "promo_code", "quantity"]
        if return_colnames:
            return rows, colnames
        else:
            return rows  # [Inventory(*row) for row in rows]

    @staticmethod
    def add_inventory(sid, pid, price_per_item, quantity, promo_code):

        mod_date = str(date.today())
        ## check if (sid, pid, price, promo_code) combo exist
        rows = app.db.execute(
            """
            SELECT * 
            FROM Inventory
            WHERE sid = :sid AND pid = :pid AND price = :price AND promo_code = :promo_code
            """,
            sid=sid,
            pid=pid,
            price=price_per_item,
            promo_code=promo_code,
        )
        if len(rows) > 0:
            # update inventory database to increase quantity by this much
            inventory_id = rows[0][0]  # find the id of the row to update
            app.db.execute(
                """
                UPDATE Inventory
                SET quantity = quantity + :quantity
                WHERE id = :id
                """,
                quantity=quantity,
                id=inventory_id,  # unique id for this row
            )
        else:
            app.db.execute(
                """
                    INSERT INTO Inventory(sid, pid, quantity, price, modified_date, promo_code)
                    VALUES(:sid, :pid, :quantity, :price, :mod_date, :promo_code)
                    """,
                sid=sid,
                pid=pid,
                quantity=quantity,
                price=price_per_item,
                mod_date=mod_date,
                promo_code=promo_code,
            )
        return True

    @staticmethod
    def remove_from_inventory(sid, pid, quantity):
        # first get current pid
        mod_date = str(date.today())
        rows = app.db.execute(
            """
            SELECT * 
            FROM Inventory
            WHERE sid = :sid AND pid = :pid
            """,
            sid=sid,
            pid=pid,
        )
        if len(rows) > 0:
            # update inventory database to increase quantity by this much
            inventory_id = rows[0][0]
            app.db.execute(
                """
                UPDATE Inventory
                SET quantity = CASE
                    WHEN quantity > :quantity THEN quantity - :quantity
                    ELSE 0 
                END
                WHERE id = :id
                """,
                quantity=quantity,
                id=inventory_id,
            )


class OrderFulfillment:
    def __init__(
        self,
        sid,
        customer_id,
        purchase_date,
        purchase_amount,
        number_items,
        fulfillment_status,
    ):
        self.sid = sid
        self.customer_id = customer_id
        self.purchase_date = purchase_date
        self.purchase_amount = purchase_amount
        self.number_items = number_items
        self.fulfillment_status = fulfillment_status

    @staticmethod
    def get_seller_orders(sid, return_colnames=False):
        rows = app.db.execute(
            """
                SELECT Orderline.id, Orderline.sid, Orderline.customer_id, Products.name, Buyer.address, Orderline.quantity, Orderline.cost_per_item * Orderline.quantity AS revenue, Orderline.fulfillment_status, Orderline.purchase_date
                FROM Orderline
                INNER JOIN Users AS Seller ON Orderline.sid = Seller.id
                INNER JOIN Users AS Buyer ON Orderline.customer_id = Buyer.id
                INNER JOIN Products ON Orderline.pid = Products.id
                WHERE Seller.id = :sid
                ORDER BY Orderline.purchase_date DESC;
            """,
            sid=sid,
        )
        if return_colnames:
            return rows, ['id', 'sid', 'customer_id', 'name', 'address', 'quantity', 'revenue', 'fulfillment_status', 'purchase_date']
        else:
            return rows

    @staticmethod
    def mark_fulfilled(orderline_id):
        mod_date = str(date.today())
        # update inventory database to increase quantity by this much
        app.db.execute(
            """
            UPDATE Orderline
            SET fulfillment_status = True, modified_date = :mod_date
            WHERE id = :id
            """,
            id=orderline_id,  # unique id for this orderline
            mod_date=mod_date,
        )
        return True

    @staticmethod
    def remove_from_inventory(sid, pid, quantity):
        # first get current pid
        mod_date = str(date.today())
        rows = app.db.execute(
            """
            SELECT * 
            FROM Inventory
            WHERE sid = :sid AND pid = :pid
            """,
            sid=sid,
            pid=pid,
        )
        if len(rows) > 0:
            # update inventory database to increase quantity by this much
            inventory_id = rows[0][0]
            app.db.execute(
                """
                UPDATE Inventory
                SET quantity = CASE
                    WHEN quantity > :quantity THEN quantity - :quantity
                    ELSE 0 
                END
                WHERE id = :id
                """,
                quantity=quantity,
                id=inventory_id,
            )

            # check if quantity is 0, if so, delete the row
            app.db.execute(
                """
                DELETE FROM Inventory
                WHERE quantity = 0
                """
            )
        return

    @staticmethod
    def get_top_sales(sid):
        rows = app.db.execute(
            """
                SELECT Orderline.sid, Orderline.pid, Products.name, SUM(Orderline.quantity) * Orderline.cost_per_item AS rev
                FROM Orderline
                INNER JOIN Products ON Orderline.pid = Products.id
                WHERE sid = :sid
                GROUP BY sid, pid, Products.name, cost_per_item
                ORDER BY rev DESC
            """,
            sid=sid,
        )
        return rows

    @staticmethod
    def get_top_customers(sid):
        rows = app.db.execute(
            """
                SELECT Orderline.sid, Orderline.customer_id, SUM(Orderline.cost_per_item * Orderline.quantity) AS rev, Users.email, Users.first_name, Users.last_name
                FROM Orderline
                INNER JOIN Users ON Orderline.customer_id = Users.id
                WHERE sid = :sid
                GROUP BY Orderline.sid, Orderline.customer_id, Users.email, Users.first_name, Users.last_name
                ORDER BY rev DESC
            """,
            sid=sid,
        )
        return rows
