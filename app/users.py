from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, InputRequired

import datetime
from flask_paginate import Pagination
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from humanize import naturaltime

from .models.seller_review import SellerReview
from .models.user import User
from .models.orderline import Orderline

from flask import Blueprint
bp = Blueprint('users', __name__)

def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

class BalanceForm(FlaskForm):
    amount = IntegerField('Amount', validators=[DataRequired(), lambda form, field: field.data >= 0 or raise_error('Amount must be a non-negative number.')])
    submit1 = SubmitField('Deposit')
    submit2 = SubmitField('Withdraw')

def raise_error(message):
    raise ValidationError(message)

class UpdateForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Update')

    def __init__(self, uid=None, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.uid = uid

    def validate_email(self, email):
        if User.email_exists_update(email.data, self.uid):
            raise ValidationError('Already a user with this email.')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(email = form.email.data,
                         password = form.password.data,
                         first_name = form.firstname.data,
                         last_name = form.lastname.data,
                         address = form.address.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/update/<uid>', methods=['GET', 'POST'])
def update(uid):
    form = UpdateForm(uid=uid)
    validated = form.validate_on_submit()
    if (not validated):
        user = User.get(uid)
        form.firstname.data = user.first_name
        form.lastname.data = user.last_name
        form.email.data = user.email
        form.address.data = user.address

        # Assign the additional data after creating the form instance
        form.uid = uid

    if validated:
        if User.update(email = form.email.data,
                         password = form.password.data,
                         first_name = form.firstname.data,
                         last_name = form.lastname.data,
                         address = form.address.data,
                         uid = uid): # there's no address field in registration, so this will be empty
            return redirect(url_for('users.accountInfoPage'))
    return render_template('updateAccountInfo.html', title='Update Account Info', form=form)



@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

@bp.route('/accountInfoPage', methods=['GET'])
def accountInfoPage():
    return render_template('accountInfoPage.html')

class UserInformationForm(FlaskForm):
    seller_id = IntegerField('User ID', validators=[InputRequired()])
    submit = SubmitField('Search')

@bp.route('/buyerSearchPage', methods=['GET', "POST"])
def buyerSearchPage():
    form = UserInformationForm()
    if form.validate_on_submit():
        return redirect(url_for('users.buyerInformation', uid=form.seller_id.data))
    return render_template('buyerSearchPage.html', title='User Search Page', form=form)


@bp.route('/accountPublicViewSearchPage', methods=['GET', "POST"])
def accountPublicViewSearchPage():
    form = UserInformationForm()
    if form.validate_on_submit():
        return redirect(url_for('users.accountPublicView', uid=form.seller_id.data))
    return render_template('accountPublicViewSearchPage.html', title='Account Search Page', form=form)




@bp.route('/accountPublicView/<uid>', methods=['GET', "POST"])
def accountPublicView(uid):
    user = User.get(uid)
    
    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page
    reviews = SellerReview.get_all_reviews_for_seller(uid)
    average_rating = SellerReview.get_average_rating(uid)
    count = 0 if reviews is None else len(reviews)
    if reviews is None: 
        reviews = []
    paginated_reviews = reviews[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=len(reviews), css_framework='bootstrap4')
    return render_template('accountPublicView.html', title='Account Public View', user=user, reviews=paginated_reviews, 
                           humanize_time=humanize_time, pagination=pagination, average_rating=average_rating, count=count)

def filter_purchases(purchases, item_filter=None, seller_filter=None, date_filter=None):
    filtered_purchases = purchases
    
    if item_filter:
        filtered_purchases = [purchase for purchase in filtered_purchases if purchase.product_name == item_filter]
    
    if seller_filter:
        filtered_purchases = [purchase for purchase in filtered_purchases if purchase.seller_name == seller_filter]
    
    if date_filter:
        filtered_purchases = [purchase for purchase in filtered_purchases if purchase.modified_date == date_filter]
    
    return filtered_purchases

@bp.route('/buyerInformation/<uid>', methods=['GET'])
def buyerInformation(uid):
    item_filter = request.args.get('item_filter')
    seller_filter = request.args.get('seller_filter')
    date_filter = request.args.get('date_filter')
    purchases = Orderline.get_all_purchases_by_uid(uid)

    # Apply filtering and render the template with filtered data
    filtered_purchases = filter_purchases(purchases, item_filter, seller_filter,date_filter)

    page = int(request.args.get('page', 1))
    per_page = 5
    offset = (page - 1) * per_page

    if filtered_purchases is None: 
        filtered_purchases = []
    paginated_filtered_purchases = filtered_purchases[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=len(filtered_purchases), css_framework='bootstrap4')

    return render_template("buyerInformation.html", purchases=paginated_filtered_purchases, uid=uid, pagination=pagination)


@bp.route('/addToAccountBalance/<uid>', methods=['GET', 'POST'])
def addToAccountBalance(uid):
    form = BalanceForm(uid=uid)

    user = User.get(uid)

    if user.balance is None:
        user.balance=0
    
    if form.validate_on_submit():
        if form.submit1.data:
            if User.Deposit(uid, form.amount.data, user.balance):
                return redirect(url_for('users.addToAccountBalance', uid=uid))
        elif form.submit2.data:
            if user.balance is None:
                user.balance=0
            if form.amount.data>user.balance:
                flash('Cannot withdraw more than balance')
                return redirect(url_for('users.addToAccountBalance', uid=uid))
            elif User.Withdraw(uid, form.amount.data, user.balance):
                return redirect(url_for('users.addToAccountBalance', uid=uid))
    
    
            
    return render_template("addToAccountBalance.html", user=user, form=form)