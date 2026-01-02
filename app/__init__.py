from flask import Flask

from .config import Config
from .deps import build_dependencies
from .routes.visitor_routes import visitor_bp
from .routes.auth_routes import auth_bp
from .routes.tenant_routes import tenant_bp
from .routes.admin_routes import admin_bp


def create_app():
    app = Flask(__name__)
    
    # Cargar configuración
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['DEBUG'] = Config.DEBUG
    
    # Construir dependencias y hacerlas disponibles en el contexto de la app
    deps = build_dependencies()
    app.config['deps'] = deps
    
    # Registro de blueprints
    app.register_blueprint(visitor_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(tenant_bp, url_prefix="/tenant")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app
