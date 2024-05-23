from flask import current_app as app
from flask import url_for

from .user import User


class SellerReview:
    def __init__(self, buyer_id, sid, rating, text, review_date):
        self.buyer_id = buyer_id
        self.sid = sid
        self.rating = rating
        self.text = text
        self.review_date = review_date

    @staticmethod
    def get_average_rating(sid):
        rows = app.db.execute(
            """
            SELECT AVG(rating)
            FROM SellerReviews s
            WHERE s.sid = :sid""",
            sid=sid,
        )
        if len(rows) == 0:
            return 0
        try:
            # return to 2 decimal points, rows[0][0] is a float
            return f"{rows[0][0]:.2f}"
        except:
            return 0
    
    def get_all_reviews_for_seller(id): 
        rows = app.db.execute(
            """
            (select buyer_id, sid, rating, text, review_date 
            from sellerreviews where sid = :id) 
            order by review_date desc;
            """,
            id=id)
        return [SellerReview(*row) for row in rows] if rows else None
        
    @staticmethod
    def get(buyer_id, sid):
        existing_review = app.db.execute('''
            SELECT * FROM SellerReviews
            WHERE buyer_id = :bid AND sid = :sid
        ''', bid=buyer_id, sid=sid)
        return existing_review[0] if (existing_review is not None) and len(existing_review) > 0 else None

    @staticmethod
    def add_update(buyer_id, sid, rating, text, review_date): #todo: composite primary key
        # Check if a review already exists
        existing_review = app.db.execute('''
            SELECT * FROM SellerReviews
            WHERE buyer_id = :bid AND sid = :sid
        ''', bid=buyer_id, sid=sid)

        if len(existing_review) > 0:
            # If a review already exists, update it (replace the existing rating/text/review)
            app.db.execute('''
                UPDATE SellerReviews
                SET rating = :rating, text = :text, review_date = :review_date
                WHERE buyer_id = :bid AND sid = :sid
            ''', bid=buyer_id, sid=sid, review_date=review_date, text=text, rating=rating)
        else:
            # Otherwise, insert a new row into the cart
            app.db.execute('''
                INSERT INTO SellerReviews(buyer_id, sid, rating, text, review_date)
                VALUES (:bid, :sid, :rating, :text, :review_date)
            ''', bid=buyer_id, sid=sid, rating=rating, text=text, review_date=review_date)

    @staticmethod
    def remove(buyer_id, sid):
        app.db.execute('''
            DELETE FROM SellerReviews
            WHERE buyer_id = :bid AND sid = :sid
        ''', bid=buyer_id, sid=sid)
