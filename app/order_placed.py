from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User
from .models.product import Product
from .models.item import Item
from .models.seller_review import SellerReview
from .models.cart import Cart
from .models.saveforlater import SaveForLater
from .seller import Inventory
from flask import request, Blueprint
from flask import jsonify
from flask import session
import numpy as np
from .models.orderline import Orderline
bp = Blueprint("order_placed", __name__)
bp2 = Blueprint("order_page", __name__)

@bp.route("/order_placed/<uid>", methods=['GET', 'POST'])
def place_order(uid):
    # Retrieve the cart associated with the user from the database and place an order for items in that cart
    if session.get('orderPlaced'):
        # Return a response indicating that the order has already been placed
        return jsonify({"message": "Order has already been placed"}), 400
    
    cart, _, cart_items2 = Cart.get_user_cart(uid)

    total = cart.get_user_total(uid)
    # update inventory in stock
    user = User.get(uid)
    # user.Deposit(uid, 500, user.balance)

    if total is None:
        return jsonify({"message": "Cart is empty"}), 400
    if user.balance is None:
        return jsonify({"message": "Insufficient funds"}), 400
    
    elif user.balance < total:
        return jsonify({"message": "Insufficient funds"}), 400

    user.Withdraw(uid,total,user.balance)
    print("balance after withdrawal", user.balance)

    for item in cart_items2:
        pid = item.pid
        quantity = item.quantity
        sid = item.sid
        price = item.price
        promo_code = item.promo_code
        inventory_list,inventory = Inventory.get_user_inventory(sid)
        seller_first_name = str(User.get(sid).first_name)
        seller_last_name = str(User.get(sid).last_name)

        for inventory_item in inventory_list:
            if inventory_item[1] == pid:
                if int(inventory_item[5]) < int(quantity):
                    return jsonify({"message": "Insufficient inventory of item: " + str(item.name) + " sold by: {} {}".format(seller_first_name, seller_last_name) + \
                                    "     desired quantity: {},    available quantity: {}".format(quantity, inventory_item[5])}, 400)
                inventory.remove_from_inventory(sid, pid, quantity)
                break
        print("removed from inventory", sid, pid, quantity)

        cart.remove_from_cart(uid, pid, sid)

    order_id = np.random.randint(100000, 999999) # generate random order_id
    rows = Orderline.get_max_id()
    orderline_id = rows[0][0] + 1
    for item in cart_items2:
        seller = User.get(item.sid)
        Orderline.add_to_orderline(orderline_id, uid, item.pid, item.sid, order_id, item.quantity, item.price, False)
        orderline_id += 1
        # increment the seller's balance
        seller.Deposit(item.sid, item.price*item.quantity, seller.balance)
        print("seller balance after deposit", seller.balance,item.sid)

    # update the balance of the buyer
    order = Orderline.get_all_purchases_by_uid_and_order_id(uid, order_id)
    # check if all items in order are fulfilled. If so, update the order status to fulfilled
    overall_fulfillment_status = True
    for item in order:
        if item.fulfillment_status == False:
            overall_fulfillment_status = False
            break
    
    return render_template("order_placed.html", cart=order, total=total, order_id = order_id, overall_fulfillment_status = overall_fulfillment_status)

@bp2.route("/order_page/<uid>/<order_id>", methods=['GET', 'POST'])
def order_page(uid, order_id):
    # get purchases by order_id, uid
    order = Orderline.get_all_purchases_by_uid_and_order_id(uid, order_id)

    total = 0
    for item in order:
        total += item.quantity * item.price

    overall_fulfillment_status = True
    for item in order:
        if item.fulfillment_status == False:
            overall_fulfillment_status = False
            break

    return render_template("order_page.html", cart=order, total=total, order_id = order_id,overall_fulfillment_status=overall_fulfillment_status)
