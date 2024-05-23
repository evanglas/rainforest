from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, id, first_name, last_name, email, password, address, balance=0):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.address = address
        self.balance = balance

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute(
            """
SELECT *
FROM Users
WHERE email = :email
""",
            email=email,
        )
        if not rows:  # email not found
            return None
        else:
            # rows is a list containing a single tuple: [(row)]
            if not check_password_hash(rows[0][4], password): # The 4th column of the row is the password column. 
                # incorrect password
                return None
            else:
                return User(*rows[0])

    @staticmethod
    def email_exists(email):
        rows = app.db.execute(
            """
SELECT email
FROM Users
WHERE email = :email
""",
            email=email,
        )
        return len(rows) > 0
    
    @staticmethod
    def email_exists_update(email, uid):
        rows = app.db.execute(
            """
SELECT email
FROM Users
WHERE email = :email
AND id != :uid
""",
            email=email,
            uid = uid
        )
        return len(rows) > 0

    @staticmethod
    def register(first_name, last_name, email, password, address):
        try:
            rows = app.db.execute(
                """
INSERT INTO Users(first_name, last_name, email, password, address)
VALUES(:first_name, :last_name, :email, :password, :address)
RETURNING id
""",
                email=email,
                address=address,
                password=generate_password_hash(password),
                first_name=first_name,
                last_name=last_name,
            )
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None
    
    @staticmethod
    def update(first_name, last_name, email, password, address, uid):
        print("fist name: ", first_name)
        try:
            rows = app.db.execute(
                """
UPDATE Users
SET first_name = :first_name,
    last_name = :last_name,
    email = :email,
    password = :password,
    address = :address
WHERE id = :uid
RETURNING id;
""",
                email=email,
                address=address,
                password=generate_password_hash(password),
                first_name=first_name,
                last_name=last_name,
                uid=uid,
            )
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    def Deposit(uid, deposit_amount, user_balance):
        print('here')
        if user_balance is None:
            user_balance=0
        try:
            rows = app.db.execute(
                """
UPDATE Users
SET balance = :new_balance
WHERE id = :uid
RETURNING id;
""",
                new_balance=user_balance+deposit_amount,
                uid=uid,
            )
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            print(str(e))
            return None
    @staticmethod
    def Withdraw(uid, withdraw_amount, user_balance):
        if user_balance is None:
            user_balance=0
        try:
            rows = app.db.execute(
                """
UPDATE Users
SET balance = :new_balance
WHERE id = :uid
RETURNING id;
""",
                new_balance=user_balance-withdraw_amount,
                uid=uid,
            )
            id = rows[0][0]
            print(id,'hii')
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute(
            """
SELECT *
FROM Users
WHERE id = :id
""",
            id=id,
        )
        return User(*(rows[0])) if rows else None
