from flask import Flask
from flask_jwt_extended import JWTManager

from config import Config

from .routes.auth import auth_bp
from .routes.cart import cart_bp
from .routes.payments import payments_bp
from .routes.products import products_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    JWTManager(app)

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(cart_bp, url_prefix="/api")
    app.register_blueprint(payments_bp, url_prefix="/api")
    app.register_blueprint(products_bp, url_prefix="/api")

    return app