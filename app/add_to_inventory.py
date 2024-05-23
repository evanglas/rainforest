from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User
from .models.product import Product
from .models.item import Item
from .models.product_review import ProductReview
from .models.cart import Cart
from .models.seller import Inventory

from flask import jsonify

from flask import Blueprint

import time

bp = Blueprint("add_to_inventory", __name__)


class InventoryAdditionForm(FlaskForm):
    pid = IntegerField('Product ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()], rounding = 2)
    promo_code = StringField('Promo code', validators = [])
    submit = SubmitField('Add product to inventory')

@bp.route('/add_to_inventory/<uid>', methods=['GET', 'POST'])
def create_form(uid):
    print(current_user.is_authenticated, file = open('out.txt', 'w'))
    print(current_user, file = open('out.txt', 'a'))
    if current_user.is_authenticated == False:
        return redirect(url_for('users.login'))
    form = InventoryAdditionForm()
    return render_template("add_to_inventory.html", form = form)

def update_form(form, uid):
    if form.is_submitted():
        if Inventory.add_inventory(sid = uid, 
                                pid = form.pid.data,
                                price_per_item = form.price.data,
                                quantity = form.quantity.data, 
                                promo_code = form.promo_code.data):
            inventory = Inventory.get_user_inventory(uid)
            return redirect("seller.html", inventory = inventory)



