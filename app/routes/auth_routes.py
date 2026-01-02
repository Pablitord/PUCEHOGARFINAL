from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from ..domain.enums import UserRole

auth_bp = Blueprint("auth", __name__)


def get_services():
    """Helper para obtener servicios desde el contexto de la app"""
    from flask import current_app
    return current_app.config.get('deps', {})


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Página de login"""
    next_url = request.args.get('next') or request.form.get('next') or url_for('visitor.home')
    
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        if not email or not password:
            flash("Email y contraseña son requeridos", "error")
            return render_template("auth/login.html", next_url=next_url)
        
        deps = get_services()
        auth_service = deps.get('auth_service')
        
        if auth_service:
            user = auth_service.login(email, password)
            if user:
                # Guardar en sesión
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['user_role'] = user.role.value
                
                # Redirigir según rol o a la URL solicitada
                if next_url and next_url != url_for('visitor.home'):
                    return redirect(next_url)
                elif user.role == UserRole.ADMIN:
                    return redirect(url_for("admin.dashboard"))
                elif user.role == UserRole.TENANT:
                    return redirect(url_for("tenant.dashboard"))
                else:
                    return redirect(url_for("visitor.home"))
            else:
                flash("Credenciales inválidas", "error")
        else:
            flash("Error en el servicio de autenticación", "error")
    
    return render_template("auth/login.html", next_url=next_url)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Página de registro"""
    next_url = request.args.get('next') or request.form.get('next') or url_for('visitor.home')
    
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")
        full_name = request.form.get("full_name", "").strip()
        
        if not email or not password:
            flash("Email y contraseña son requeridos", "error")
            return render_template("auth/register.html", next_url=next_url)
        
        if password != password_confirm:
            flash("Las contraseñas no coinciden", "error")
            return render_template("auth/register.html", next_url=next_url)
        
        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres", "error")
            return render_template("auth/register.html", next_url=next_url)
        
        deps = get_services()
        auth_service = deps.get('auth_service')
        
        if auth_service:
            try:
                # Registrar como TENANT por defecto
                user = auth_service.register(
                    email=email,
                    password=password,
                    full_name=full_name if full_name else None,
                    role=UserRole.TENANT
                )
                
                # Iniciar sesión automáticamente
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['user_role'] = user.role.value
                
                flash("¡Registro exitoso! Bienvenido a PUCEHOGAR", "success")
                
                # Redirigir según la URL solicitada o al dashboard
                if next_url and next_url != url_for('visitor.home'):
                    return redirect(next_url)
                else:
                    return redirect(url_for("tenant.dashboard"))
            except ValueError as e:
                flash(str(e), "error")
            except Exception as e:
                flash(f"Error al registrar: {str(e)}", "error")
        else:
            flash("Error en el servicio de autenticación", "error")
    
    return render_template("auth/register.html", next_url=next_url)


@auth_bp.route("/logout")
def logout():
    """Cerrar sesión"""
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("visitor.home"))


def require_auth(f):
    """Decorador para requerir autenticación"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Debes iniciar sesión para acceder a esta página", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def require_role(role: UserRole):
    """Decorador para requerir un rol específico"""
    from functools import wraps
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Debes iniciar sesión para acceder a esta página", "warning")
                return redirect(url_for("auth.login"))
            
            user_role = session.get('user_role')
            if user_role != role.value:
                flash("No tienes permisos para acceder a esta página", "error")
                return redirect(url_for("visitor.home"))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
