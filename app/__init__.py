from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB

from logging import FileHandler, WARNING

login = LoginManager()
login.login_view = "users.login"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.db = DB(app)
    login.init_app(app)

    from .index import bp as index_bp

    app.register_blueprint(index_bp)

    from .users import bp as user_bp

    app.register_blueprint(user_bp)

    from .product import bp as product_bp

    app.register_blueprint(product_bp)

    from .seller import bp as seller_bp

    app.register_blueprint(seller_bp)

    from .seller_analytics import bp as seller_analytics_bp

    app.register_blueprint(seller_analytics_bp)

    from .reviews import bp as reviews_bp

    app.register_blueprint(reviews_bp)

    from .cart import bp as cart_bp

    app.register_blueprint(cart_bp)

    from .order_placed import bp as order_placed_bp

    app.register_blueprint(order_placed_bp)

    from .order_placed import bp2 as place_order_bp

    app.register_blueprint(place_order_bp)

    from .add_product import bp as add_product_bp

    app.register_blueprint(add_product_bp)

    from .edit_product import bp as edit_product_bp

    app.register_blueprint(edit_product_bp)

    app.jinja_env.add_extension("jinja2.ext.loopcontrols")
    app.jinja_env.globals.update(enumerate=enumerate)
    file_handler = FileHandler("errorlog.txt")
    file_handler.setLevel(WARNING)

    return app
