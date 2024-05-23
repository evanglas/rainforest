from flask import current_app as app

class SaveForLater:
    def __init__(self, uid, pid, sid, price, quantity, promo_code):
        self.uid = uid
        self.pid = pid
        self.sid = sid
        self.price = price
        self.quantity = quantity
        self.promo_code = promo_code

    @staticmethod
    def get(uid):
        rows = app.db.execute('''
            SELECT uid, name, price
            FROM SaveForLater
            WHERE id = :uid
            ''',
            id=uid)
        return SaveForLater(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_user_saveforlater(uid):
        rows = app.db.execute('''SELECT SaveForLater.* as name FROM SaveForLater where SaveForLater.uid = :uid ORDER BY SaveForLater.pid ASC''', uid=uid)
        names = app.db.execute('''SELECT Products.short_name as name FROM SaveForLater, Products WHERE SaveForLater.uid = :uid and Products.id = SaveForLater.pid ORDER BY SaveForLater.pid ASC''', uid=uid)
        rows = [row for row in rows]  # Convert rows to a list of tuples
        names = [name for name, in names]  # Convert names to a list of strings
        rows_and_names = [(row[0], row[1], row[2], row[3], row[4], row[5], name) for row, name in zip(rows, names)]
        SaveForLater_items = app.db.execute('''
    SELECT SaveForLater.*, 
           Products.short_name as name, 
           Users.first_name as seller_first_name, 
           Users.last_name as seller_last_name
    FROM SaveForLater, Products, Users 
    WHERE SaveForLater.uid = :uid 
    AND Products.id = SaveForLater.pid 
    AND Users.id = SaveForLater.sid 
    ORDER BY SaveForLater.pid ASC
''', uid=uid)
        # return [SaveForLater(*row) for row in rows_and_names]
        if len(rows) > 0:
            return SaveForLater(*(rows[0])), rows_and_names, SaveForLater_items
        else:
            return SaveForLater, [], []

    @staticmethod
    def add_to_saveforlater(uid, pid, sid, price, quantity, promo_code):
        # Check if the product is already in the SaveForLater
        existing_saveforlater_item = app.db.execute('''
            SELECT * FROM SaveForLater
            WHERE uid = :uid AND pid = :pid AND sid = :sid
        ''', uid=uid, pid=pid, sid=sid)

        if len(existing_saveforlater_item) > 0:
            # If the product is already in the SaveForLater, update the quantity
            new_quantity = int(existing_saveforlater_item[0][4]) + int(quantity)
            app.db.execute('''
                UPDATE SaveForLater
                SET quantity = :new_quantity
                WHERE uid = :uid AND pid = :pid AND sid = :sid
            ''', new_quantity=new_quantity, uid=uid, pid=pid, sid=sid)
        else:
            # Otherwise, insert a new row into the SaveForLater
            app.db.execute('''
                INSERT INTO SaveForLater(uid, pid, sid, price, quantity, promo_code)
                VALUES (:uid, :pid, :sid, :price, :quantity, :promo_code)
            ''', uid=uid, pid=pid, sid=sid, price=price, quantity=quantity, promo_code=promo_code)

    @staticmethod
    def remove_from_saveforlater(uid, pid, sid):
        app.db.execute('''
            DELETE FROM SaveForLater
            WHERE uid = :uid AND pid = :pid AND sid = :sid
        ''', uid=uid, pid=pid, sid=sid)

    def remove_from_saveforlater_and_add_to_cart(uid, pid, sid, price, quantity, promo_code):
        app.db.execute('''
            DELETE FROM SaveForLater
            WHERE uid = :uid AND pid = :pid AND sid = :sid
        ''',uid=uid, pid=pid, sid=sid)
        app.db.execute('''
            INSERT INTO Cart(id, uid, pid, sid, price, quantity, promo_code)
            VALUES (:uid, :pid, :sid, :price, :quantity, :promo_code)
        ''', uid=uid, pid=pid, sid=sid, price=price, quantity=quantity, promo_code=promo_code)

    @staticmethod
    def get_user_total(uid):
        rows = app.db.execute('''
SELECT SUM(SaveForLater.price * SaveForLater.quantity)
FROM SaveForLater
WHERE uid = :uid
''',
                              uid=uid)
        return rows[0][0]

    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT * FROM SaveForLater
''')
        return [SaveForLater(*row) for row in rows]