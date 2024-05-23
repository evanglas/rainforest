from flask import current_app as app
from flask import url_for


class Item_Listing:
    def __init__(self, short_name, pid, price, quantity, image_src):
        self.short_name = short_name
        self.pid = pid
        self.price = price
        self.quantity = quantity
        self.image_src = image_src

    @staticmethod
    # Returns the item in the inventory with the lowest price for each product. In the case of ties, picks the item with the highest listed quantity.
    def get_cheapest_items():
        rows = app.db.execute(
            """
                SELECT p.short_name, i.pid, i.price, i.quantity, p.image_src
                FROM Inventory i
                JOIN Products p ON i.pid = p.id
                WHERE (i.pid, i.price, i.quantity) IN (
                    SELECT pid, MIN(price), MAX(quantity)
                    FROM Inventory
                    GROUP BY pid
                )
            """,
        )
        print(url_for("static", filename="images/" + rows[0][4]))
        return [Item_Listing(*row) for row in rows]
