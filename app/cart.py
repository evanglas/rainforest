from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User
from .models.product import Product
from .models.item import Item
from .models.product_review import ProductReview
from .models.cart import Cart
from .models.saveforlater import SaveForLater
from .flask_paginate_new import Pagination
from flask import Blueprint

bp = Blueprint("cart", __name__)

@bp.route("/cart/<uid>", methods=['GET', 'POST'])
def cart(uid):
    # Retrieve the cart associated with the user from the database

    # delete items from cart if the user clicks the delete button
    if request.method == 'POST':
        # Retrieve data from form
        uid = request.form.get('uid')
        sid = request.form.get('sid')
        pid = request.form.get('pid')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        promo_code = request.form.get('promo_code')
        update_quantity = request.form.get('update_quantity')
        is_cart = request.form.get('is_cart')
        # Ensure all required data is provided
        if uid is None or sid is None or pid is None or quantity is None:
            return "Missing required data", 400
        # Remove item from cart
        if is_cart == 'true':
            user_cart,_,cart_items = Cart.get_user_cart(uid)
            user_cart.remove_from_cart(uid, pid, sid)
            user_cart,_,cart_items = Cart.get_user_cart(uid)
        elif is_cart == 'false':
            user_saveforlater,_,saveforlater_items = SaveForLater.get_user_saveforlater(uid)
            user_saveforlater.remove_from_saveforlater(uid, pid, sid)
        
        if update_quantity == '1':
            print("quantity", quantity)
            user_cart,_,cart_items = Cart.get_user_cart(uid)
            user_cart.add_to_cart(uid, pid, sid, price, 1, promo_code)
            user_cart,_,cart_items = Cart.get_user_cart(uid)
        elif update_quantity == '-1':
            if int(quantity) - 1 > 0:
                user_cart,_,cart_items = Cart.get_user_cart(uid)
                user_cart.add_to_cart(uid, pid, sid, price, -1, promo_code)

    _, _, cart_items = Cart.get_user_cart(uid)
    _, _, saveforlater_items = SaveForLater.get_user_saveforlater(uid)

    page_cart = int(request.args.get('page_cart', 1))
    page_savedforlater = int(request.args.get('page_savedforlater', 1))

    per_page = 5

    offset_cart = (page_cart - 1) * per_page
    offset_savedforlater = (page_savedforlater - 1) * per_page

    paginated_cart_items = cart_items[offset_cart: offset_cart + per_page] 

    pagination_cart = Pagination(page=page_cart, per_page=per_page, total=len(cart_items), css_framework='bootstrap4', page_parameter = 'page_cart')

    paginated_saveforlater_items = saveforlater_items[offset_savedforlater: offset_savedforlater + per_page]
    pagination_saveforlater = Pagination(page=page_savedforlater, per_page=per_page, total=len(saveforlater_items), \
                                         css_framework='bootstrap4', page_parameter = 'page_savedforlater')
    total = Cart.get_user_total(uid)
    total_saveforlater = SaveForLater.get_user_total(uid)
    return render_template("cart.html", cart=paginated_cart_items, saveforlater = paginated_saveforlater_items, \
                           total=total, total_saveforlater = total_saveforlater, pagination_cart = pagination_cart, \
                            pagination_saveforlater = pagination_saveforlater)
