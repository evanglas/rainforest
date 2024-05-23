from flask import current_app as app
from flask import url_for

from .user import User


class ProductReview:
    def __init__(self, uid, pid, rating, text, review_date):
        self.uid = uid
        self.pid = pid
        self.rating = rating
        self.text = text
        self.review_date = review_date

    @staticmethod
    def get_product_reviews_and_reviewers(pid):
        rows = app.db.execute(
            """
SELECT *
FROM ProductReviews p JOIN Users u ON p.uid = u.id
WHERE p.pid = :pid
ORDER BY p.rating DESC, p.review_date DESC
""",
            pid=pid,
        )
        return [ProductReview(*row[:5]) for row in rows], [
            User(*row[5:]) for row in rows
        ]

    @staticmethod
    def get_average_rating(pid):
        rows = app.db.execute(
            """
            SELECT AVG(rating)
            FROM ProductReviews p
            WHERE p.pid = :pid""",
            pid=pid,
        )
        if len(rows) == 0:
            return 0
        try:
            # return to 2 decimal points, rows[0][0] is a float
            return f"{rows[0][0]:.2f}"
        except:
            return 0
        
    @staticmethod
    def get(uid, pid):
        existing_review = app.db.execute('''
            SELECT * FROM ProductReviews
            WHERE uid = :uid AND pid = :pid
        ''', uid=uid, pid=pid)
        return existing_review[0] if (existing_review is not None) and len(existing_review) > 0 else None

    @staticmethod
    def add_update(uid, pid, rating, text, review_date): #todo: composite primary key
        # Check if a review already exists
        existing_review = app.db.execute('''
            SELECT * FROM ProductReviews
            WHERE uid = :uid AND pid = :pid
        ''', uid=uid, pid=pid)

        if len(existing_review) > 0:
            # If a review already exists, update it (replace the existing rating/text/review)
            app.db.execute('''
                UPDATE ProductReviews
                SET rating = :rating, text = :text, review_date = :review_date
                WHERE uid = :uid AND pid = :pid
            ''', uid=uid, pid=pid, review_date=review_date, text=text, rating=rating)
        else:
            # Otherwise, insert a new row into the cart
            app.db.execute('''
                INSERT INTO ProductReviews(uid, pid, rating, text, review_date)
                VALUES (:uid, :pid, :rating, :text, :review_date)
            ''', uid=uid, pid=pid, rating=rating, text=text, review_date=review_date)

    @staticmethod
    def remove(uid, pid):
        app.db.execute('''
            DELETE FROM ProductReviews
            WHERE uid = :uid AND pid = :pid
        ''', uid=uid, pid=pid)

    @staticmethod
    def get_num_reviews(pid):
        rows = app.db.execute(
            """
            SELECT COUNT(*)
            FROM ProductReviews p
            WHERE p.pid = :pid""",
            pid=pid,
        )
        return rows[0][0]
