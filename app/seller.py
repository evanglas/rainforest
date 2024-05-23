from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DecimalField, HiddenField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User
from .models.product import Product
from .models.item import Item
from .models.product_review import ProductReview
from .models.cart import Cart
from .models.seller import Inventory, OrderFulfillment
from .flask_paginate_new import Pagination

from flask import jsonify

from flask import Blueprint

import time

bp = Blueprint("seller", __name__)


class InventoryAdditionForm(FlaskForm):
    sid = HiddenField()
    pid = SelectField('Product ID', validators = [DataRequired()])
    quantity = IntegerField('How much do you want to change the quantity in inventory by? (positive for addition, negative for deletion)', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()], rounding = 2)
    promo_code = StringField('Promo code', validators=[])
    submit = SubmitField('Add product to inventory')

    def __init__(self, *args, **kwargs):
        super(InventoryAdditionForm, self).__init__(*args, **kwargs)
        # Populate choices for the SubmitField from the database
        self.pid.choices = Product.get_pids()

    def validate_price(self, price):
        # try:
        rows, cols = Inventory.get_user_product(
            sid = self.sid.data, 
            pid = int(self.pid.data),
            return_colnames = True
        )
        if(len(rows) == 0):
            flash('Adding new product.')
        else:
            item = rows[0]
            if item[cols.index('price')] != self.price.data:
                raise ValidationError('Price of products in inventory is $' + str(item[cols.index('price')]) + ', which does not match price you want to add: $' + str(price.data))

    def validate_quantity(self, quantity):
        # try:
        rows, cols = Inventory.get_user_product(
            sid = self.sid.data,
            pid = int(self.pid.data),
            return_colnames = True
        )
        if(len(rows) == 0):
            if quantity.data < 0:
                raise ValidationError('This product does not exist. You cannot add negative items.')
            flash('Adding new product.')
        else:
            if rows[0][cols.index('quantity')] < -quantity.data:
                raise ValidationError('You cannot delete more items than you have in your inventory, which is currently', quantity, 'items')

class InventoryUpdateForm(FlaskForm):
    sid = HiddenField()
    pid = SelectField('Product ID', validators = [DataRequired()])
    quantity = IntegerField('How much do you want to change the quantity in inventory by? (positive for addition, negative for deletion)', validators=[DataRequired()])
    price = DecimalField('Price (read only)', validators=[DataRequired()], rounding = 2, render_kw={'readonly' : True})
    promo_code = StringField('Promo code (read only)', validators=[], render_kw={'readonly' : True})
    submit = SubmitField('Add product to inventory')


    def __init__(self, *args, **kwargs):
        super(InventoryUpdateForm, self).__init__(*args, **kwargs)
        # Populate choices for the SubmitField from the database
        self.pid.choices = Product.get_pids()

    def validate_price(self, price):
        # try:
        print('pid', self.pid.data)
        rows, cols = Inventory.get_user_product(
            sid = self.sid.data, 
            pid = int(self.pid.data),
            return_colnames = True
        )

        item = rows[0]
        print('item', item)
        if item[cols.index('price')] != self.price.data:
            raise ValidationError('Price of products in inventory is $' + str(item[cols.index('price')]) + ', which does not match price you want to add: $' + str(price.data))

    def validate_quantity(self, quantity):
        rows, cols = Inventory.get_user_product(
            sid = self.sid.data,
            pid = int(self.pid.data),
            return_colnames = True
        )
        print('rows', rows)
        if(len(rows) == 0):
            flash('Adding new product.')
        else:
            if rows[0][cols.index('quantity')] < -quantity.data:
                raise ValidationError('You cannot delete more items than you have in your inventory, which is currently ' + str(rows[0][cols.index('quantity')]) + ' items')


def update_products(form, uid):
    Inventory.add_inventory(sid = uid, 
                            pid = form.pid.data,
                            price_per_item = form.price.data,
                            quantity = form.quantity.data, 
                            promo_code = form.promo_code.data)

@bp.route("/seller/<uid>/<action>", methods=['GET', 'POST'])
def seller(uid, action):

    #### actions for current inventory
    form = InventoryAdditionForm(sid = uid)
    inventory, inventory_cols = Inventory.get_user_inventory(uid, return_colnames = True)
   

    inventory_page = request.args.get('inventory_page', 1, int)
    per_page = 5
    offset = (inventory_page - 1) * per_page
    paginated_inventory_items = inventory[offset: offset + per_page]
    pagination_inventory = Pagination(page=inventory_page, per_page=per_page, total=len(inventory), css_framework='bootstrap4', page_parameter = 'inventory_page')
    pagination_inventory.page = request.args.get('inventory_page', 1, int)
    
    if 'edit' in action:
        edit_pid = int(action.split('=')[1])
        item, inventory_cols = Inventory.get_user_product(sid = uid, pid = edit_pid, return_colnames = True)
        if len(item) == 0:
            form = InventoryAdditionForm(sid = uid,
                                     pid = edit_pid,
                                     quantity = 0)
            flash('This item is not in inventory currently. Describe what price and promo code you\'d like to sell the product at.')
        else:
            item = item[0]
            form = InventoryUpdateForm(sid = uid,
                                        pid = edit_pid,
                                        quantity = 0, #item[inventory_cols.index('quantity')],
                                        price = float(item[inventory_cols.index('price')]),
                                        promo_code = item[inventory_cols.index('promo_code')])
    elif 'delete' in action:
        delete_pid = int(action.split('=')[1])
        item = Inventory.get_user_product(sid = uid, pid = delete_pid)[0]
        Inventory.add_inventory(
            sid = item[inventory_cols.index('sid')], 
            pid = item[inventory_cols.index('pid')], 
            price_per_item = item[inventory_cols.index('price')], 
            quantity = -1 * item[inventory_cols.index('quantity')], ## we delete items by subtracting current quantity amount
            promo_code = item[inventory_cols.index('promo_code')])
        return redirect(url_for('seller.seller', uid=uid, action = "all"))

    #### actions for order fulfillment
    orderline, orderline_cols = OrderFulfillment.get_seller_orders(sid = uid, return_colnames = True)
    orderline_page = request.args.get('orderline_page', 1, int)

    orderline_offset = (orderline_page - 1) * per_page
    paginated_orderline_items = orderline[orderline_offset : orderline_offset + per_page]
    pagination_orderline = Pagination(page=5, per_page=per_page, total=len(orderline), css_framework='bootstrap4', page_parameter = 'orderline_page')


    ### add action for fulfillment
    if 'fulfill' in action:
        fulfill_orderline_id = int(action.split('=')[1])
        OrderFulfillment.mark_fulfilled(fulfill_orderline_id)
        return redirect(url_for('seller.seller', uid=uid, action = "all"))

    ### add pagination

    if form.validate_on_submit():
        update_products(form, uid)
        return redirect(url_for('seller.seller', uid=uid, action = "all"))
    else:
        print(form.errors)
    
    return render_template("seller.html", inventory=paginated_inventory_items, orderline = paginated_orderline_items, form = form, pagination = pagination_inventory, pagination_orderline = pagination_orderline)

