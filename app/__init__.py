from flask import Flask, session, g, request

from .config import Config
from .deps import build_dependencies
from .routes.visitor_routes import visitor_bp
from .routes.auth_routes import auth_bp
from .routes.tenant_routes import tenant_bp
from .routes.admin_routes import admin_bp
from .services.notification_service import NotificationService


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

    @app.context_processor
    def inject_notifications():
        user_id = session.get("user_id")
        deps = app.config.get("deps", {})
        notification_service: NotificationService = deps.get("notification_service")
        notifications = []
        if user_id and notification_service:
            notifications = notification_service.get_unread(user_id, limit=8)
        return {
            "notifications_unread": notifications,
            "notifications_count": len(notifications) if notifications else 0,
        }

    @app.before_request
    def mark_notification_as_read():
        notif_id = request.args.get("notif_id")
        user_id = session.get("user_id")
        if notif_id and user_id:
            deps = app.config.get("deps", {})
            notification_service: NotificationService = deps.get("notification_service")
            if notification_service:
                notification_service.mark_as_read(notif_id, user_id)

    return app
