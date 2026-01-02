from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from ..domain.enums import DepartmentStatus, UserRole
from .auth_routes import require_auth

visitor_bp = Blueprint("visitor", __name__)


def get_services():
    """Helper para obtener servicios desde el contexto de la app"""
    from flask import current_app
    return current_app.config.get('deps', {})


@visitor_bp.route("/")
def home():
    """Página principal: catálogo de departamentos disponibles con filtros"""
    deps = get_services()
    department_service = deps.get('department_service')

    filters = {}
    # Características
    if request.args.get("has_terrace") == "1":
        filters["has_terrace"] = True
    if request.args.get("has_balcony") == "1":
        filters["has_balcony"] = True
    if request.args.get("sea_view") == "1":
        filters["sea_view"] = True
    if request.args.get("parking") == "1":
        filters["parking"] = True
    if request.args.get("furnished") == "1":
        filters["furnished"] = True
    # Rangos
    def _parse_float(val):
        try:
            return float(val)
        except Exception:
            return None
    def _parse_int(val):
        try:
            return int(val)
        except Exception:
            return None
    min_price = _parse_float(request.args.get("min_price"))
    max_price = _parse_float(request.args.get("max_price"))
    min_rooms = _parse_int(request.args.get("min_rooms"))
    max_rooms = _parse_int(request.args.get("max_rooms"))
    if min_price is not None:
        filters["min_price"] = min_price
    if max_price is not None:
        filters["max_price"] = max_price
    if min_rooms is not None:
        filters["min_rooms"] = min_rooms
    if max_rooms is not None:
        filters["max_rooms"] = max_rooms

    if department_service:
        departments = department_service.get_all_departments(
            available_only=True,
            filters=filters if filters else None
        )
    else:
        departments = []

    active_filters = {
        "has_terrace": filters.get("has_terrace", False),
        "has_balcony": filters.get("has_balcony", False),
        "sea_view": filters.get("sea_view", False),
        "parking": filters.get("parking", False),
        "furnished": filters.get("furnished", False),
        "min_price": request.args.get("min_price", "") or "",
        "max_price": request.args.get("max_price", "") or "",
        "min_rooms": request.args.get("min_rooms", "") or "",
        "max_rooms": request.args.get("max_rooms", "") or "",
    }

    return render_template(
        "visitor/departments.html",
        departments=departments,
        active_filters=active_filters
    )


@visitor_bp.route("/department/<department_id>")
def department_detail(department_id: str):
    """Detalle de un departamento"""
    deps = get_services()
    department_service = deps.get('department_service')
    
    if department_service:
        department = department_service.get_department_by_id(department_id)
        if not department:
            flash("Departamento no encontrado", "error")
            return redirect(url_for("visitor.home"))
    else:
        department = None
        flash("Error al cargar el departamento", "error")
        return redirect(url_for("visitor.home"))
    
    # Verificar si el usuario está autenticado
    is_authenticated = 'user_id' in session
    user_id = session.get('user_id') if is_authenticated else None
    
    return render_template(
        "visitor/department_detail.html",
        department=department,
        is_authenticated=is_authenticated,
        user_id=user_id
    )


@visitor_bp.route("/department/<department_id>/pay", methods=["GET", "POST"])
def pay_department(department_id: str):
    """Pagar un departamento (crear pago y subir comprobante)"""
    # Requerir autenticación
    if 'user_id' not in session:
        flash("Debes iniciar sesión para realizar un pago", "warning")
        return redirect(url_for("auth.login", next=url_for("visitor.pay_department", department_id=department_id)))
    
    user_id = session.get('user_id')
    deps = get_services()
    
    department_service = deps.get('department_service')
    payment_service = deps.get('payment_service')
    
    # Verificar que el departamento existe
    department = department_service.get_department_by_id(department_id)
    if not department:
        flash("Departamento no encontrado", "error")
        return redirect(url_for("visitor.home"))
    
    if request.method == "POST":
        amount = request.form.get("amount")
        month = request.form.get("month")
        notes = request.form.get("notes", "")
        
        if 'receipt' not in request.files:
            flash("Debes subir un comprobante de pago", "error")
            return render_template("visitor/pay_department.html", department=department)
        
        file = request.files['receipt']
        if file.filename == '':
            flash("Debes seleccionar un archivo", "error")
            return render_template("visitor/pay_department.html", department=department)
        
        try:
            file_content = file.read()
            if len(file_content) == 0:
                flash("El archivo está vacío", "error")
                return render_template("visitor/pay_department.html", department=department)
            
            # Validar tamaño (máx 10MB)
            max_size = 10 * 1024 * 1024  # 10MB
            if len(file_content) > max_size:
                flash("El archivo es demasiado grande. Máximo 10MB", "error")
                return render_template("visitor/pay_department.html", department=department)
            
            # Crear pago con comprobante
            payment = payment_service.create_payment_with_receipt(
                tenant_id=user_id,
                department_id=department_id,
                amount=float(amount),
                month=month,
                file_content=file_content,
                file_name=file.filename,
                notes=notes if notes else None
            )
            
            if payment:
                flash("Pago registrado correctamente. Está pendiente de revisión.", "success")
                return redirect(url_for("visitor.department_detail", department_id=department_id))
            else:
                flash("Error al registrar el pago", "error")
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
    
    return render_template("visitor/pay_department.html", department=department)
