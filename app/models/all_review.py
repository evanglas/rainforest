from flask import current_app as app
from datetime import datetime

class Review: 
    def __init__(self, reviewer_id, product_id, seller_id, rating, text, review_date):
        self.reviewer_id = reviewer_id
        self.product_id = product_id # null if not a product review
        self.seller_id = seller_id # null if not a seller review
        self.rating = rating
        self.text = text
        self.review_date = review_date
    
    def get_most_recent(id, count=5): 
        rows = app.db.execute(
            """
            (select uid, pid, NULL as seller_id, rating, text, review_date 
            from productreviews where uid = :id) 
            UNION 
            (select buyer_id, NULL as product_id, sid, rating, text, review_date 
            from sellerreviews where buyer_id = :id) 
            order by review_date desc limit :count;
            """,
            id=id, count=count)
        return [Review(*row) for row in rows] if rows else None
    
    def get_all(id): 
        rows = app.db.execute(
            """
            (select uid, pid, NULL as seller_id, rating, text, review_date 
            from productreviews where uid = :id) 
            UNION 
            (select buyer_id, NULL as product_id, sid, rating, text, review_date 
            from sellerreviews where buyer_id = :id) 
            order by review_date desc;
            """,
            id=id)
        return [Review(*row) for row in rows] if rows else None


