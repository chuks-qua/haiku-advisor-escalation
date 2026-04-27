from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///orders.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "dev-only-change-me"
    if config:
        app.config.update(config)

    db.init_app(app)

    from api.orders import bp as orders_bp
    from api.auth import bp as auth_bp

    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
