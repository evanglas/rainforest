from flask import current_app as app
from .purchase import Purchase


class Orderline:
    def __init__(self, id, customer_id, pid, sid, order_id, quantity, cost_per_item, fulfillment_status, purchase_date, modified_date):
        self.id = id
        self.customer_id = customer_id
        self.pid = pid
        self.sid = sid
        self.order_id = order_id
        self.quantity = quantity
        self.cost_per_item = cost_per_item
        self.fulfillment_status = fulfillment_status
        self._date = purchase_date
        self.modified_date = modified_date

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, customer_id, pid, sid, order_id, quantity, cost_per_item, fulfillment_status, modified_date
FROM Orderline
WHERE id = :id
''',
                              id=id)
        return Orderline(*(rows[0])) if rows else None

    @staticmethod
    def get_all_purchases_by_uid(uid):
        rows = app.db.execute('''
SELECT u.first_name buyer_name, p.name as product_name, u1.first_name as seller_name, o.quantity, o.cost_per_item, o.fulfillment_status, o.modified_date, o.order_id
FROM Orderline o, Products p, Users u, Users u1
WHERE o.customer_id = :uid
AND p.id = o.pid
and u.id = o.customer_id
AND u1.id = o.sid
ORDER BY modified_date DESC
''',
                              uid=uid)
        return [Purchase(*row) for row in rows]
    
    @staticmethod
    def add_to_orderline(id, customer_id, pid, sid, order_id, quantity, cost_per_item, fulfillment_status):
        app.db.execute('''
INSERT INTO Orderline (id, customer_id, pid, sid, order_id,quantity, cost_per_item, fulfillment_status)
VALUES (:id, :customer_id, :pid, :sid, :order_id, :quantity, :cost_per_item, :fulfillment_status)
''',
                       id=id, customer_id=customer_id, pid=pid, sid=sid, order_id=order_id, quantity=quantity, cost_per_item=cost_per_item, fulfillment_status=fulfillment_status)
        return
    @staticmethod
    def update_fulfillment_status(customer_id,pid,sid,order_id,fulfillment_status):
        app.db.execute(''' UPDATE Orderline SET fulfillment_status = :fulfillment_status WHERE customer_id = :customer_id AND pid = :pid AND sid = :sid AND id = :order_id''',
                       customer_id=customer_id, pid=pid, sid=sid, order_id=order_id, fulfillment_status=fulfillment_status)
        return
    
    @staticmethod
    def get_max_id():
        rows = app.db.execute('''SELECT MAX(id) FROM Orderline''')
        return rows

    @staticmethod
    def get_all_purchases_by_uid_and_order_id(uid, order_id):
        rows = app.db.execute('''SELECT Orderline.id, customer_id as uid, pid, sid, order_id, quantity, cost_per_item as price, fulfillment_status, modified_date, 
                              Users.first_name as seller_first_name,
           Users.last_name as seller_last_name, Products.short_name as name from Orderline, Users, Products
                              where customer_id = :uid and order_id = :order_id and Users.id = Orderline.sid and Products.id = Orderline.pid''',
                              uid=uid, order_id=order_id)

        return rows
    @staticmethod
    def bought_from(buyer_id, seller_id):
        rows = app.db.execute(
            """
            SELECT * FROM Orderline
            WHERE customer_id = :buyer_id AND sid = :seller_id
            """,
            buyer_id=buyer_id, seller_id=seller_id
        )
        return len(rows) > 0
