from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime, date

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
    if request.args.get("allow_pets") == "1":
        filters["allow_pets"] = True
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
        "allow_pets": filters.get("allow_pets", False),
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
    payment_service = deps.get('payment_service')
    notification_service = deps.get('notification_service')
    auth_service = deps.get('auth_service')
    email_service = deps.get('email_service')
    
    if department_service:
        department = department_service.get_department_by_id(department_id)
        if not department:
            flash("Departamento no encontrado", "error")
            return redirect(url_for("visitor.home"))
    else:
        department = None
        flash("Error al cargar el departamento", "error")
        return redirect(url_for("visitor.home"))
    
    # Verificar si el usuario está autenticado y si ya tiene un pago para este depto
    is_authenticated = 'user_id' in session
    user_id = session.get('user_id') if is_authenticated else None
    existing_payment_status = None
    if is_authenticated and payment_service:
        payments = payment_service.get_payments_by_tenant(user_id)
        for p in payments:
            if p.department_id == department_id:
                existing_payment_status = p.status.value
                break
    
    return render_template(
        "visitor/department_detail.html",
        department=department,
        is_authenticated=is_authenticated,
        user_id=user_id,
        existing_payment_status=existing_payment_status
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
    notification_service = deps.get('notification_service')
    auth_service = deps.get('auth_service')
    email_service = deps.get('email_service')
    
    # Verificar que el departamento existe
    department = department_service.get_department_by_id(department_id)
    if not department:
        flash("Departamento no encontrado", "error")
        return redirect(url_for("visitor.home"))
    
    def _month_key(d: date) -> int:
        return d.year * 12 + d.month

    def _is_month_allowed(month_str: str) -> bool:
        try:
            m_date = datetime.strptime(month_str, "%Y-%m").date()
            today = date.today()
            max_key = _month_key(today)
            min_key = max_key - 2  # hasta dos meses atrás
            max_allowed = max_key + 1  # hasta un mes después
            return min_key <= _month_key(m_date) <= max_allowed
        except Exception:
            return False

    if request.method == "POST":
        amount = request.form.get("amount")
        month = request.form.get("month")
        notes = request.form.get("notes", "")
        start_date_str = request.form.get("start_date")
        end_date_str = request.form.get("end_date")
        expected_amount = float(department.price)
        
        if 'receipt' not in request.files:
            flash("Debes subir un comprobante de pago", "error")
            return render_template("visitor/pay_department.html", department=department)
        
        file = request.files['receipt']
        if file.filename == '':
            flash("Debes seleccionar un archivo", "error")
            return render_template("visitor/pay_department.html", department=department)
        
        try:
            # Validar monto numérico
            try:
                amount_val = float(amount)
            except Exception:
                flash("Monto inválido", "error")
                return render_template("visitor/pay_department.html", department=department)

            file_content = file.read()
            if len(file_content) == 0:
                flash("El archivo está vacío", "error")
                return render_template("visitor/pay_department.html", department=department)
            
            # Validar tamaño (máx 10MB)
            max_size = 10 * 1024 * 1024  # 10MB
            if len(file_content) > max_size:
                flash("El archivo es demasiado grande. Máximo 10MB", "error")
                return render_template("visitor/pay_department.html", department=department)

            # Calcular monto prorrateado si se ingresa rango de fechas
            if start_date_str or end_date_str:
                if not start_date_str or not end_date_str:
                    flash("Debes elegir fecha de inicio y fin para la reserva", "error")
                    return render_template("visitor/pay_department.html", department=department)
                try:
                    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                    end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                    if end_dt < start_dt:
                        raise ValueError("La fecha fin no puede ser menor que la fecha inicio")
                    delta_days = (end_dt - start_dt).days + 1
                    if delta_days < 1 or delta_days > 30:
                        raise ValueError("El rango de reserva debe ser entre 1 y 30 días")
                    daily_rate = float(department.price) / 30
                    expected_amount = round(daily_rate * delta_days, 2)
                    amount_val = expected_amount  # ajustamos al prorrateo
                    extra_note = f"[Reserva {start_dt.strftime('%d/%m')} - {end_dt.strftime('%d/%m')} ({delta_days} días)]"
                    notes = f"{extra_note} {notes}".strip()
                except ValueError as e:
                    flash(str(e), "error")
                    return render_template("visitor/pay_department.html", department=department)
            else:
                # Sin fechas, el mínimo requerido es el precio mensual completo
                expected_amount = float(department.price)

            # Validar que el monto no sea menor al requerido
            if amount_val < expected_amount:
                flash(f"El monto no puede ser menor a ${expected_amount:.2f}", "error")
                return render_template("visitor/pay_department.html", department=department)

            # Validar mes de pago (hasta 1 mes después y hasta 2 meses atrás)
            if not month or not _is_month_allowed(month):
                flash("El mes de pago debe estar entre 2 meses atrás y 1 mes después del mes actual", "error")
                return render_template("visitor/pay_department.html", department=department)
            
            # Crear pago con comprobante
            payment = payment_service.create_payment_with_receipt(
                tenant_id=user_id,
                department_id=department_id,
                amount=amount_val,
                month=month,
                file_content=file_content,
                file_name=file.filename,
                notes=notes if notes else None
            )
            
            if payment:
                tenant_user = auth_service.get_user_by_id(user_id) if auth_service else None
                # Notificar a todos los admins (evitar duplicados por email repetido)
                if notification_service and auth_service:
                    admins = auth_service.user_repo.get_admins()
                    sent_admin_emails = set()
                    for admin in admins:
                        notification_service.create(
                            user_id=admin.id,
                            title="Nuevo pago/reserva",
                            message=f"Se registró un pago para {department.title}",
                            link=url_for("admin.payment_detail", payment_id=payment.id, _external=False),
                            type="payment_created"
                        )
                        if email_service and admin.email and admin.email not in sent_admin_emails:
                            email_service.send_email(
                                [admin.email],
                                "Nuevo pago/reserva registrado",
                                f"Se registró un pago/reserva.\n\n"
                                f"Departamento: {department.title}\n"
                                f"Monto: ${amount_val:.2f}\n"
                                f"Mes: {month}\n"
                                f"Notas: {notes or 'N/A'}\n"
                                f"Usuario: {tenant_user.email if tenant_user else 'N/D'}\n\n"
                                f"Revisa el detalle en el panel de administración."
                            )
                            sent_admin_emails.add(admin.email)
                # Confirmar al usuario que su pago quedó registrado (pendiente)
                if email_service and auth_service:
                    tenant = auth_service.get_user_by_id(user_id)
                    if tenant and tenant.email:
                        email_service.send_email(
                            [tenant.email],
                            "Pago/reserva registrado",
                            f"Hemos recibido tu pago/reserva.\n\n"
                            f"Departamento: {department.title}\n"
                            f"Monto: ${amount_val:.2f}\n"
                            f"Mes: {month}\n"
                            f"Notas: {notes or 'N/A'}\n"
                            f"Estado: Pendiente de revisión\n\n"
                            f"Gracias por tu pago. Te avisaremos cuando sea aprobado."
                        )
                flash("Pago registrado correctamente. Está pendiente de revisión.", "success")
                return redirect(url_for("visitor.department_detail", department_id=department_id))
            else:
                flash("Error al registrar el pago", "error")
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
    
    return render_template("visitor/pay_department.html", department=department)
