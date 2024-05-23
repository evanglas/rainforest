from flask import render_template, request, session
from flask_paginate import Pagination, get_page_parameter

from .models.item import Item
from .models.category import Category

from flask import Blueprint

bp = Blueprint("index", __name__)

SORT_OPTIONS = {
    "Price: Low to High": "price ASC",
    "Price: High to Low": "price DESC",
    "Avg Rating: High to Low": "avg_rating DESC",
    "Avg Rating: Low to High": "avg_rating ASC",
    "Name A-Z": "short_name ASC",
    "Name Z-A": "short_name DESC",
}

LIMIT_CHOICES = [10, 25, 50, 100]


@bp.route("/", methods=["GET", "POST"])
def index():

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = request.args.get("per_page", 10, type=int)

    session["sort_by"] = request.args.get("sort_by", "Price: Low to High")
    session["k"] = request.args.get("limit", 10)

    elementId = request.args.get("elementId", None)

    if elementId == "filterButton":
        session["price_min"] = request.args.get("price_min")
        session["price_max"] = request.args.get("price_max")
        category = request.args.get("category")
        session["category"] = request.args.get("category")
        session["avg_product_rating_min"] = request.args.get("avg_product_rating_min")
        session["avg_seller_rating_min"] = request.args.get("avg_seller_rating_min")
    elif elementId == "searchQuery":
        session["search_query"] = request.args.get("search_query")
    elif elementId == "clearFilterButton":
        print("hi")
        session.pop("price_min", None)
        session.pop("price_max", None)
        session.pop("category", None)
        session.pop("avg_product_rating_min", None)
        session.pop("avg_seller_rating_min", None)
        session.pop("search_query", None)

    sort_by = session.get("sort_by")
    price_min = session.get("price_min")
    price_max = session.get("price_max")
    avg_product_rating_min = session.get("avg_product_rating_min")
    avg_seller_rating_min = session.get("avg_seller_rating_min")
    category_id = session.get("category", 0)
    category = Category.get(category_id)
    cat_left_idx = category.left
    cat_right_idx = category.right
    search_query = session.get("search_query", "")

    filter_by = {
        "price_min": price_min,
        "price_max": price_max,
        "cat_left_idx": cat_left_idx,
        "cat_right_idx": cat_right_idx,
        "avg_product_rating_min": avg_product_rating_min,
        "avg_seller_rating_min": avg_seller_rating_min,
        "search_query": search_query,
    }

    (
        landing_items,
        landing_products,
        product_categories,
        product_ratings,
        rating_counts,
    ) = Item.get_cheapest_items_and_products(
        sortBy=SORT_OPTIONS[sort_by], filterBy=filter_by, k=None
    )

    pagination = Pagination(
        page=page,
        per_page=per_page,
        total=len(landing_items),
        css_framework="bootstrap4",
    )

    child_categories = Category.get_next_level(category_id)
    parent_categories = Category.get_previous_levels(category_id)
    print([p.name for p in parent_categories])

    filter_fields = {
        key: value for key, value in filter_by.items() if value is not None
    }

    offset = (page - 1) * per_page
    return render_template(
        "index.html",
        landing_items=landing_items[offset : offset + per_page],
        landing_products=landing_products[offset : offset + per_page],
        sort_options=SORT_OPTIONS,
        sort_by=sort_by,
        filter=filter_fields,
        limit_options=LIMIT_CHOICES,
        limit_choice=per_page,
        category=category,
        child_categories=child_categories,
        parent_categories=parent_categories,
        pagination=pagination,
        product_ratings=product_ratings,
        rating_counts=rating_counts,
        search_query=search_query,
    )
