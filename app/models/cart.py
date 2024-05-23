from flask import current_app as app

class Cart:
    def __init__(self, uid, pid, sid, price, quantity, promo_code):
        self.uid = uid
        self.pid = pid
        self.sid = sid
        self.price = price
        self.quantity = quantity
        self.promo_code = promo_code

    @staticmethod
    def get(uid, pid, sid):
        rows = app.db.execute('''
            SELECT uid, name, price
            FROM Cart
            WHERE uid = :uid AND pid = :pid AND sid = :sid
            ''',
            id=id, uid=uid, pid=pid, sid=sid)
        return Cart(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_user_cart(uid):
        
        rows = app.db.execute('''SELECT Cart.* as name FROM Cart where Cart.uid = :uid ORDER BY Cart.pid ASC''', uid=uid)
        names = app.db.execute('''SELECT Products.short_name as name FROM Cart, Products WHERE Cart.uid = :uid and Products.id = Cart.pid ORDER BY Cart.pid ASC''', uid=uid)
        rows = [row for row in rows]  # Convert rows to a list of tuples
        names = [name for name, in names]  # Convert names to a list of strings
        rows_and_names = [(row[0], row[1], row[2], row[3], row[4], row[5], name) for row, name in zip(rows, names)]
        cart_items = app.db.execute('''
    SELECT Cart.*, 
           Products.short_name as name, 
           Users.first_name as seller_first_name, 
           Users.last_name as seller_last_name
    FROM Cart, Products, Users 
    WHERE Cart.uid = :uid 
    AND Products.id = Cart.pid 
    AND Users.id = Cart.sid 
    ORDER BY Cart.pid ASC
''', uid=uid)
        # return [Cart(*row) for row in rows_and_names]
        if len(rows) > 0:
            return Cart(*(rows[0])), rows_and_names, cart_items
        else:
            return Cart, [], []

    @staticmethod
    def add_to_cart(uid, pid, sid, price, quantity, promo_code):
        
        # Check if the product is already in the cart
        existing_cart_item = app.db.execute('''
            SELECT * FROM Cart
            WHERE uid = :uid AND pid = :pid AND sid = :sid
        ''', uid=uid, pid=pid, sid=sid)

        if len(existing_cart_item) > 0:
            # If the product is already in the cart, update the quantity
            new_quantity = int(existing_cart_item[0][4]) + int(quantity)
            try:
                app.db.execute('''
                    UPDATE Cart
                    SET quantity = :new_quantity
                    WHERE uid = :uid AND pid = :pid AND sid = :sid
                ''', new_quantity=new_quantity, uid=uid, pid=pid, sid=sid)
            except:
                pass
        else:
            # Otherwise, insert a new row into the cart
                app.db.execute('''
                    INSERT INTO Cart(uid, pid, sid, price, quantity, promo_code)
                    VALUES (:uid, :pid, :sid, :price, :quantity, :promo_code);
                ''',uid=uid, pid=pid, sid=sid, price=price, quantity=quantity, promo_code=promo_code)

    @staticmethod
    def remove_from_cart(uid, pid, sid):
        app.db.execute('''
            DELETE FROM Cart
            WHERE uid = :uid AND pid = :pid AND sid = :sid
        ''', uid=uid, pid=pid, sid=sid)

    @staticmethod
    def get_user_total(uid):
        rows = app.db.execute('''
SELECT SUM(Cart.price * Cart.quantity)
FROM Cart
WHERE uid = :uid
''',
                              uid=uid)
        return rows[0][0]
    
    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT * FROM Cart
''')
        return [Cart(*row) for row in rows]