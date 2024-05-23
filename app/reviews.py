from flask import render_template, redirect, url_for, flash
from flask_login import current_user
from flask import jsonify
import datetime
from flask_paginate import Pagination
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, InputRequired, ValidationError

from .models.all_review import Review
from .models.product_review import ProductReview
from .models.seller_review import SellerReview
from .models.orderline import Orderline

from humanize import naturaltime

def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

from flask import Blueprint
bp = Blueprint('reviews', __name__)

@bp.route('/user_reviews')
def user_reviews():
    if current_user.is_authenticated: 
        reviews = Review.get_all(current_user.id)
        page = int(request.args.get('page', 1))
        per_page = 5
        offset = (page - 1) * per_page
        if reviews is not None: 
            paginated_reviews = reviews[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(reviews), css_framework='bootstrap4')
            return render_template('user_reviews.html', reviews=paginated_reviews, humanize_time=humanize_time, pagination=pagination)
        else: 
            return render_template('user_reviews.html', reviews=None, humanize_time=humanize_time)
    else: 
        return render_template('user_reviews.html', reviews=None, humanize_time=humanize_time)
class review_lookup(FlaskForm):
    uid = IntegerField('Reviewer ID', validators=[InputRequired(), lambda form, field: field.data >= 0 or raise_error('Reviewer IDs are non-negative integers')])
    submit = SubmitField('Search')

@bp.route('/reviewsearch', methods=['GET', "POST"])
def reviewsearch():
    form = review_lookup()
    if form.validate_on_submit():
        return redirect(url_for('reviews.reviews', uid=form.uid.data))
    return render_template('reviewsearch.html', form=form)

@bp.route('/reviews/<uid>', methods = ['GET'])
def reviews(uid):
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page
    reviews = Review.get_all(uid)
    if reviews is None: 
        reviews = []
    paginated_reviews = reviews[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=len(reviews), css_framework='bootstrap4')
    return render_template('review.html', reviews=paginated_reviews, humanize_time=humanize_time, pagination=pagination)

def raise_error(message):
    raise ValidationError(message)

class ReviewForm(FlaskForm):
    rating = IntegerField('Rating (1-5)', validators=[DataRequired(), lambda form, field: field.data >= 1 and field.data <= 5 or raise_error('Rating must be 1, 2, 3, 4, or 5')])
    text = StringField('Review Text', validators=[DataRequired()])    
    submit = SubmitField('Submit')
    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete', name='submit_delete')

@bp.route('/product-reviews/<uid>/<pid>/update', methods = ['GET', 'POST'])
def updateProductReview(uid, pid):
    if current_user.is_authenticated and int(current_user.id) == int(uid): 
        form = ReviewForm()
        deleter = DeleteForm()
        validated = form.validate_on_submit()
        deleted = 'submit_delete' in request.form
        if deleted:
            ProductReview.remove(uid, pid)
            return redirect(url_for('reviews.user_reviews'))
        else: 
            if not validated:
                review = ProductReview.get(uid, pid)
                if review is not None: 
                    form.rating.data = review.rating
                    form.text.data = review.text
            if validated:
                review_date = datetime.datetime.now()
                ProductReview.add_update(uid, pid, form.rating.data, form.text.data, review_date)
                return redirect(url_for('reviews.user_reviews'))
        return render_template('updateReview.html', form=form, deleter=deleter, subtitle=f'for Product {pid}')
    else: 
        return redirect(url_for('users.login'))
    
@bp.route('/seller-reviews/<buyer_id>/<sid>/update', methods = ['GET', 'POST'])
def updateSellerReview(buyer_id, sid):
    if current_user.is_authenticated and int(current_user.id) == int(buyer_id): 
        if Orderline.bought_from(buyer_id, sid): 
            form = ReviewForm()
            deleter = DeleteForm()
            validated = form.validate_on_submit()
            deleted = 'submit_delete' in request.form
            if deleted:
                SellerReview.remove(buyer_id, sid)
                return redirect(url_for('reviews.user_reviews'))
            else:
                if not validated:
                    review = SellerReview.get(buyer_id, sid)
                    if review is not None: 
                        form.rating.data = review.rating
                        form.text.data = review.text
                if validated:
                    review_date = datetime.datetime.now()
                    ProductReview.add_update(buyer_id, sid, form.rating.data, form.text.data, review_date)
                    return redirect(url_for('reviews.user_reviews'))
            return render_template('updateReview.html', form=form, deleter=deleter, subtitle=f'for Seller {sid}')
        else: 
            return render_template('error.html', message=f'You must have bought from this seller (Seller {sid}) to leave a review.')
    else: 
        return redirect(url_for('users.login'))