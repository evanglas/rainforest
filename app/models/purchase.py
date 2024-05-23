from flask import current_app as app

class Purchase:
    def __init__(self, buyer_name, product_name, seller_name, quantity, cost_per_item, fulfillment_status, modified_date, order_id):
        self.buyer_name = buyer_name
        self.product_name = product_name
        self.seller_name = seller_name
        self.quantity = quantity
        self.cost_per_item = cost_per_item
        self.fulfillment_status = fulfillment_status
        self.modified_date = modified_date
        self.order_id = order_id