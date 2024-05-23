from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse

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

import pandas as pd

bp = Blueprint("seller_analytics", __name__)



@bp.route("/seller_analytics/<uid>/<action>", methods=['GET', 'POST'])
def seller_analytics(uid, action):
    ### get a priori analysis
    top_sales = OrderFulfillment.get_top_sales(uid)
    top_sales_page = int(request.args.get('top_sales_page', 1))
    per_page = 3
    offset = (top_sales_page - 1) * per_page
    paginated_top_sales = top_sales[offset: offset + per_page] 
    pagination_top_sales = Pagination(page=top_sales_page, per_page=per_page, total=len(top_sales), css_framework='bootstrap4', page_parameter = 'top_sales_page')
    pagination_top_sales.page = request.args.get('top_sales_page', 1, int)

    top_customers = OrderFulfillment.get_top_customers(uid)
    top_customers_page = int(request.args.get('top_customers_page', 1))
    per_page = 3
    top_customers_offset = (top_customers_page - 1) * per_page
    paginated_top_customers = top_customers[top_customers_offset : top_customers_offset + per_page]
    pagination_top_customers = Pagination(page = top_customers_page, per_page = per_page, total = len(top_customers), css_framework = 'bootstrap4', page_parameter = 'top_customers_page')
    pagination_top_customers.page = request.args.get('top_customers_page', 1, int)

    return render_template("seller_analytics.html", top_sales = paginated_top_sales, pagination_top_sales = pagination_top_sales, pagination_top_customers = pagination_top_customers, top_customers = paginated_top_customers)

