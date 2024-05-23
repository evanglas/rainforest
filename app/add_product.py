from flask import render_template, redirect, url_for, flash, request
from .models.product import Product
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import InputRequired
from flask_login import current_user
from flask import current_app as app

from flask import Blueprint
import numpy as np

bp = Blueprint("add_product", __name__)


class AddForm(FlaskForm):
    product_name = StringField("Product Name", validators=[InputRequired()])
    product_short_name = StringField("Short Name", validators=[InputRequired()])
    product_description = StringField("Description", validators=[InputRequired()])
    submit = SubmitField("Add Product")


@bp.route("/add_product", methods=["GET", "POST"])
def add_product():
    form = AddForm()

    if request.method == "POST" and form.validate():
        product = Product.add(
            form.product_name.data,
            form.product_short_name.data,
            form.product_description.data,
            "https://picsum.photos/id/" + str(np.random.randint(1, 85)) + "/1000",
            current_user.id,
        )
        app.db.execute(
            """
                INSERT INTO ProductCategory (id, category_id)
                VALUES (:product_id, :category_id)
            """,
            product_id=product.id,
            category_id=3,
        )
        flash(f"Product {product.name} added successfully")

    return render_template("add_product.html", form=form)
