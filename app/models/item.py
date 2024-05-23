from flask import current_app as app
from .user import User
from .product import Product
from .product_review import ProductReview
from .category import Category


class Item:

    def __init__(
        self,
        id,
        sid,
        pid,
        quantity,
        price,
        modified_date=None,
        promo_code=None,
    ):
        self.id = id
        self.sid = sid
        self.pid = pid
        self.quantity = quantity
        self.price = price
        self.modified_date = modified_date
        self.promo_code = promo_code

    def serialize(self):
        return {
            "id": self.id,
            "price": str(
                self.price
            ),  # convert decimal to string for JSON serialization
        }

    @staticmethod
    def get(id):
        rows = app.db.execute(
            """
                SELECT *
                FROM Inventory
                WHERE id = :id
            """,
            id=id,
        )
        return Item(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_cheapest_items_and_products(k=None, sortBy=None, filterBy=None):
        base_query = f"""
                SELECT *
                FROM Inventory i
                JOIN Products p ON i.pid = p.id
                LEFT JOIN (SELECT AVG(rating) as avg_rating, pid FROM ProductReviews GROUP BY pid) pr ON i.pid = pr.pid
                LEFT JOIN ProductCategory pc on p.id = pc.id
                LEFT JOIN Categories c on pc.category_id = c.id
                WHERE (i.pid, i.price, i.quantity) IN (
                    SELECT pid, MIN(price), MAX(quantity)
                    FROM Inventory
                    GROUP BY pid
                )
            """
        if filterBy is not None:
            if filterBy["search_query"]:
                base_query += f" AND (p.name ILIKE '%{filterBy['search_query']}%' OR p.description ILIKE '%{filterBy['search_query']}%')"
            if filterBy["price_min"]:
                base_query += f" AND i.price >= {filterBy['price_min']}"
            if filterBy["price_max"]:
                base_query += f" AND i.price <= {filterBy['price_max']}"
            if filterBy["avg_product_rating_min"]:
                base_query += (
                    f" AND pr.avg_rating >= {filterBy['avg_product_rating_min']}"
                )
            if filterBy["cat_left_idx"] and filterBy["cat_right_idx"]:
                base_query += f" AND c.left_idx >= {filterBy['cat_left_idx']} AND c.right_idx <= {filterBy['cat_right_idx']}"
            if filterBy["avg_seller_rating_min"]:
                base_query += f" AND i.sid IN (SELECT sid FROM SellerReviews WHERE avg_rating >= {filterBy['avg_seller_rating_min']})"
            if sortBy is not None:
                base_query += f" ORDER BY {sortBy} NULLS LAST"
            if k is not None:
                base_query += f" LIMIT {k}"

        rows = app.db.execute(
            base_query,
        )
        return (
            [Item(*row[:7]) for row in rows],
            [Product(*row[7:13]) for row in rows],
            [Category(*row[17:]) for row in rows],
            [ProductReview.get_average_rating(row[2]) for row in rows],
            [ProductReview.get_num_reviews(row[2]) for row in rows],
        )

    # Gets list of sellers of items with same pid, seller, and price.
    def get_items_and_sellers(pid):
        rows = app.db.execute(
            """
                SELECT i.sid, i.pid, sum(i.quantity), i.price
                FROM Inventory i
                WHERE i.pid = :pid
                GROUP BY i.sid, i.pid, i.price
            """,
            pid=pid,
        )
        return [Item(-1, row[0], row[1], row[2], row[3], None, None) for row in rows], [
            User.get(row[0]) for row in rows
        ]

    # Get product with desired sid and pid
    def get_product_from_particular_seller(sid, pid):
        rows = app.db.execute(
            """
            
                SELECT i.id, i.sid, i.pid, i.quantity, i.price, i.modified_date, i.promo_code
                FROM Inventory i
                WHERE sid = :sid AND pid = :pid
            """,
            sid=sid,
            pid=pid,
        )
        return Item(*(rows[0])) if rows is not None else None
