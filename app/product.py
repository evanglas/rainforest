from flask import render_template, redirect, url_for, flash, request,get_flashed_messages

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from flask import current_app as app
from .models.product import Product
from .models.item import Item
from .models.product_review import ProductReview
from .models.cart import Cart
from .models.saveforlater import SaveForLater
from flask import request
from flask import Blueprint

class AddtoCart(FlaskForm):
    add_to_cart = SubmitField('Add to Cart')

bp = Blueprint("product", __name__)
from .flask_paginate_new import Pagination

@bp.route('/product/<pid>', methods=['POST', 'GET'])
def retrieve_product(pid):

    """Retrieve the product with a given PID and render the HTML template.
    If a POST request is detected, add this product to the user's cart. """

    product = Product.get(pid)
    items, sellers = Item.get_items_and_sellers(pid)
    product_reviews, reviewers = ProductReview.get_product_reviews_and_reviewers(pid)
    average_review = ProductReview.get_average_rating(pid)
    num_review = len(product_reviews)

    page_sellers = int(request.args.get('page_sellers', 1))
    page_product_reviews = int(request.args.get('page_product_reviews', 1))

    per_page = 5
    offset_sellers = (page_sellers - 1) * per_page
    offset_product_reviews = (page_product_reviews - 1) * per_page

    paginated_product_reviews = product_reviews[offset_product_reviews: offset_product_reviews + per_page]
    paginated_reviewers = reviewers[offset_product_reviews: offset_product_reviews + per_page]
    paginated_sellers = sellers[offset_sellers: offset_sellers + per_page]
    paginated_items = items[offset_sellers: offset_sellers + per_page]

    if product is None:
        return redirect(url_for("index.index"))

    flashed_messages = []
    existing_quantity_in_cart = None

    if request.method == 'POST':
        # Retrieve data from form
        uid = request.form.get('uid')
        _,_,user_cart = Cart.get_user_cart(uid)
        sid = request.form.get('sid')
        quantity = request.form.get('quantity')
        # prev_quantity = request.form.get('prev_quantity')
        is_wishlist = request.form.get('wishlist')
        remove_from_wishlist = request.form.get('remove_from_wishlist')
        # Ensure all required data is provided
        if uid is None or sid is None or quantity is None:
            return "Missing required data", 400  # Bad request

        try:
            quantity = int(quantity)
        except ValueError:
            return "Invalid quantity", 400  # Bad request
        
        if is_wishlist=='true':
            saveforlater,_,_ = SaveForLater.get_user_saveforlater(uid)
            
            product_item = Item.get_product_from_particular_seller(sid, pid)
            if quantity == 0:
                new_items = []
                new_sellers = []
                new_reviewers = []
                new_product_reviews = []
                for i in range(len(items)):
                    if items[i].quantity != 0:
                        new_items.append(items[i])
                        new_sellers.append(sellers[i])
                items = new_items
                sellers = new_sellers
                reviewers = new_reviewers
                product_reviews = new_product_reviews
                saveforlater.remove_from_saveforlater(saveforlater.id, uid, pid, sid)
            else:
                existing_saveforlater_item = app.db.execute('''
                    SELECT * FROM SaveForLater
                    WHERE uid = :uid AND pid = :pid AND sid = :sid
                ''', uid=uid, pid=pid, sid=sid)
                existing_quantity_in_saveforlater = existing_saveforlater_item[0][4] if len(existing_saveforlater_item) > 0 else 0
                if quantity + existing_quantity_in_saveforlater > product_item.quantity:
                    print("Not enough stock available. You already have {} items of this type in SaveForLater.".format(existing_quantity_in_saveforlater))
                    return redirect(url_for("product.retrieve_product", pid=pid))
                else:
                    # id = str(uid) + '.' + str(pid) + '.' + str(sid)
                    saveforlater.add_to_saveforlater(uid, pid, sid, product_item.price, quantity, product_item.promo_code)

        else:
            cart, _,_ = Cart.get_user_cart(uid)
            product_item = Item.get_product_from_particular_seller(sid, pid)
            if quantity == 0:
                new_items = []
                new_sellers = []
                new_reviewers = []
                new_product_reviews = []
                for i in range(len(items)):
                    if items[i].quantity != 0:
                        new_items.append(items[i])
                        new_sellers.append(sellers[i])
                items = new_items
                sellers = new_sellers
                reviewers = new_reviewers
                product_reviews = new_product_reviews
                cart.remove_from_cart(uid, pid, sid)
            else:
                existing_cart_item = app.db.execute('''
                    SELECT * FROM Cart
                    WHERE uid = :uid AND pid = :pid AND sid = :sid
                ''', uid=uid, pid=pid, sid=sid)
                existing_quantity_in_cart = existing_cart_item[0][4] if len(existing_cart_item) > 0 else 0
                if quantity + existing_quantity_in_cart > product_item.quantity:
                    print("Not enough stock available. You already have {} items of this type in Cart.".format(existing_quantity_in_cart))
                    return redirect(url_for("product.retrieve_product", pid=pid))
                else:
                    id = str(uid) + '.' + str(pid) + '.' + str(sid)
                    cart.add_to_cart(uid, pid, sid, product_item.price, quantity, product_item.promo_code)
                    # remove from wishlist
                    saveforlater,_,_ = SaveForLater.get_user_saveforlater(uid)
                    if remove_from_wishlist == 'true':
                        saveforlater.remove_from_saveforlater(uid, pid, sid)
                    

    return render_template(
        "product.html",
        product=product,
        items=paginated_items,
        sellers=paginated_sellers,
        product_reviews=paginated_product_reviews,
        reviewers=paginated_reviewers,
        average_review=str(average_review),
        existing_quantity_in_cart = existing_quantity_in_cart,
        flashed_messages = flashed_messages, 
        pagination_product_reviews = Pagination(record_name='product',page_parameter='page_product_reviews',page=page_product_reviews, per_page=per_page, total=len(product_reviews), css_framework='bootstrap4'),
        pagination_sellers = Pagination(record_name='product',page_parameter='page_sellers', page=page_sellers, per_page=per_page, total=len(sellers), css_framework='bootstrap4'), 
        num_review = str(num_review)
    )

