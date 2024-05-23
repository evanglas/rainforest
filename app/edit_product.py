from flask import render_template, redirect, url_for, flash, request
from .models.product import Product
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import InputRequired
import numpy as np

from flask import jsonify

from flask import Blueprint
from flask_login import current_user

bp = Blueprint("edit_product", __name__)


class EditForm(FlaskForm):
    product_id = SelectField("Product ID", validators=[InputRequired()])
    product_name = StringField("Product Name", validators=[InputRequired()])
    product_short_name = StringField("Short Name", validators=[InputRequired()])
    product_description = StringField("Description", validators=[InputRequired()])
    submit = SubmitField("Edit Product")

    def __init__(self):
        super(EditForm, self).__init__()
        self.product_id.choices = Product.get_pids(current_user.id)


@bp.route("/edit_product", methods=["GET", "POST"])
def edit_product():
    form = EditForm()

    if request.method == "POST" and form.validate():
        Product.update(
            form.product_id.data,
            form.product_name.data,
            form.product_short_name.data,
            form.product_description.data,
            "https://picsum.photos/id/" + str(np.random.randint(1, 85)) + "/1000",
        )
        flash(f"Product {form.product_id.data} updated successfully")

    form.product_id.choices = Product.get_pids(current_user.id)
    return render_template("edit_product.html", form=form)
