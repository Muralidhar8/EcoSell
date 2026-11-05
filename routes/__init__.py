from .main_routes import main_bp
from .auth_routes import auth_bp
from .seller_routes import seller_bp
from .buyer_routes import buyer_bp
from .admin_routes import admin_bp

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(buyer_bp)
    app.register_blueprint(admin_bp)

