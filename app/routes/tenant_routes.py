from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime

from .auth_routes import require_auth
from ..domain.enums import UserRole, PaymentStatus
from ..domain.entities import Payment

tenant_bp = Blueprint("tenant", __name__)


def get_services():
    """Helper para obtener servicios desde el contexto de la app"""
    from flask import current_app
    return current_app.config.get('deps', {})


def get_current_user_id():
    """Obtiene el ID del usuario actual desde la sesión"""
    return session.get('user_id')


@tenant_bp.route("/dashboard")
@require_auth
def dashboard():
    """Panel del inquilino"""
    user_id = get_current_user_id()
    deps = get_services()

    auth_service = deps.get('auth_service')
    department_service = deps.get('department_service')
    payment_service = deps.get('payment_service')
    report_service = deps.get('report_service')

    user = auth_service.get_user_by_id(user_id) if auth_service else None

    payments = payment_service.get_payments_by_tenant(user_id) if payment_service else []
    reports = report_service.get_reports_by_tenant(user_id) if report_service else []

    def _sort_dt(value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return datetime.min

    payments = sorted(payments, key=lambda p: _sort_dt(getattr(p, "created_at", None)), reverse=True)
    reports = sorted(reports, key=lambda r: _sort_dt(getattr(r, "created_at", None)), reverse=True)

    def _tenant_departments(user_obj, payment_list):
        ids = set()
        if user_obj and user_obj.department_id:
            ids.add(user_obj.department_id)
        for p in payment_list:
            if hasattr(p, "status") and p.status.value == PaymentStatus.APPROVED.value:
                ids.add(p.department_id)
        departments = []
        if department_service:
            for dep_id in ids:
                dept = department_service.get_department_by_id(dep_id)
                if dept:
                    departments.append(dept)
        return departments

    departments = _tenant_departments(user, payments)
    department = departments[0] if departments else None

    return render_template(
        "tenant/dashboard.html",
        user=user,
        department=department,
        departments=departments,
        payments=payments,
        reports=reports
    )


@tenant_bp.route("/payment/new", methods=["GET", "POST"])
@require_auth
def new_payment():
    """Crear un nuevo pago"""
    user_id = get_current_user_id()
    deps = get_services()
    auth_service = deps.get('auth_service')
    payment_service = deps.get('payment_service')
    department_service = deps.get('department_service')
    notification_service = deps.get('notification_service')

    user = auth_service.get_user_by_id(user_id) if auth_service else None
    payments = payment_service.get_payments_by_tenant(user_id) if payment_service else []

    def _tenant_departments(user_obj, payment_list):
        ids = set()
        if user_obj and user_obj.department_id:
            ids.add(user_obj.department_id)
        for p in payment_list:
            if hasattr(p, "status") and p.status.value == PaymentStatus.APPROVED.value:
                ids.add(p.department_id)
        departments = []
        if department_service:
            for dep_id in ids:
                dept = department_service.get_department_by_id(dep_id)
                if dept:
                    departments.append(dept)
        return departments

    departments = _tenant_departments(user, payments)

    if request.method == "POST":
        amount = request.form.get("amount")
        month = request.form.get("month")
        notes = request.form.get("notes", "")
        department_id = request.form.get("department_id")

        if not departments:
            flash("No tienes un departamento asignado", "error")
            return redirect(url_for("tenant.dashboard"))

        if not department_id:
            department_id = departments[0].id
        else:
            valid_ids = [d.id for d in departments]
            if department_id not in valid_ids:
                flash("Departamento no válido", "error")
                return render_template("tenant/new_payment.html", departments=departments)

        # Validar comprobante obligatorio
        if 'receipt' not in request.files:
            flash("Debes subir un comprobante de pago", "error")
            return render_template("tenant/new_payment.html", departments=departments)
        file = request.files['receipt']
        if file.filename == '':
            flash("Debes seleccionar un archivo de comprobante", "error")
            return render_template("tenant/new_payment.html", departments=departments)

        try:
            file_content = file.read()
            if len(file_content) == 0:
                flash("El archivo está vacío", "error")
                return render_template("tenant/new_payment.html", departments=departments)
            if len(file_content) > 10 * 1024 * 1024:
                flash("El archivo es demasiado grande. Máximo 10MB", "error")
                return render_template("tenant/new_payment.html", departments=departments)

            payment = payment_service.create_payment_with_receipt(
                tenant_id=user_id,
                department_id=department_id,
                amount=float(amount),
                month=month,
                file_content=file_content,
                file_name=file.filename,
                notes=notes if notes else None
            )
            # Notificar a admins
            if payment and notification_service and auth_service:
                admins = auth_service.user_repo.get_admins()
                for admin in admins:
                    notification_service.create(
                        user_id=admin.id,
                        title="Nuevo pago/reserva",
                        message=f"Se registró un pago para {departments[0].title if departments else 'un departamento'}",
                        link=url_for("admin.payment_detail", payment_id=payment.id, _external=False),
                        type="payment_created"
                    )
            flash("Pago registrado correctamente. Está pendiente de revisión.", "success")
            return redirect(url_for("tenant.dashboard"))
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error al crear el pago: {str(e)}", "error")
    
    # GET: mostrar formulario
    if not departments:
        flash("No tienes un departamento asignado o aprobado para pagar", "error")
        return redirect(url_for("tenant.dashboard"))

    return render_template("tenant/new_payment.html", departments=departments)


@tenant_bp.route("/payment/<payment_id>/receipt", methods=["GET", "POST"])
@require_auth
def upload_receipt(payment_id: str):
    """Subir comprobante de pago"""
    user_id = get_current_user_id()
    deps = get_services()
    payment_service = deps.get('payment_service')
    
    # Verificar que el pago pertenece al usuario
    payment = payment_service.get_payment_by_id(payment_id)
    if not payment or payment.tenant_id != user_id:
        flash("Pago no encontrado", "error")
        return redirect(url_for("tenant.dashboard"))
    
    if request.method == "POST":
        if 'receipt' not in request.files:
            flash("No se seleccionó ningún archivo", "error")
            return render_template("tenant/upload_receipt.html", payment=payment)
        
        file = request.files['receipt']
        if file.filename == '':
            flash("No se seleccionó ningún archivo", "error")
            return render_template("tenant/upload_receipt.html", payment=payment)
        
        try:
            file_content = file.read()
            if len(file_content) == 0:
                flash("El archivo está vacío", "error")
                return render_template("tenant/upload_receipt.html", payment=payment)
            
            # Validar tamaño (máx 10MB)
            max_size = 10 * 1024 * 1024  # 10MB
            if len(file_content) > max_size:
                flash("El archivo es demasiado grande. Máximo 10MB", "error")
                return render_template("tenant/upload_receipt.html", payment=payment)
            
            updated_payment = payment_service.upload_receipt(
                payment_id=payment_id,
                file_content=file_content,
                file_name=file.filename
            )
            if updated_payment:
                flash("Comprobante subido correctamente", "success")
                return redirect(url_for("tenant.dashboard"))
            else:
                flash("Error al subir el comprobante", "error")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
    
    return render_template("tenant/upload_receipt.html", payment=payment)


@tenant_bp.route("/payment/<payment_id>")
@require_auth
def payment_detail(payment_id: str):
    """Detalle de pago para inquilino"""
    user_id = get_current_user_id()
    deps = get_services()
    payment_service = deps.get('payment_service')
    auth_service = deps.get('auth_service')
    department_service = deps.get('department_service')

    payment = payment_service.get_payment_by_id(payment_id) if payment_service else None
    if not payment or payment.tenant_id != user_id:
        flash("Pago no encontrado", "error")
        return redirect(url_for("tenant.dashboard"))

    department = department_service.get_department_by_id(payment.department_id) if department_service else None
    admin = auth_service.get_user_by_id(payment.reviewed_by) if auth_service and payment.reviewed_by else None

    return render_template(
        "tenant/payment_detail.html",
        payment=payment,
        department=department,
        admin=admin
    )


@tenant_bp.route("/report/new", methods=["GET", "POST"])
@require_auth
def new_report():
    """Crear un nuevo reporte"""
    user_id = get_current_user_id()
    deps = get_services()
    
    auth_service = deps.get('auth_service')
    if not auth_service:
        flash("Error en el servicio", "error")
        return redirect(url_for("tenant.dashboard"))
    
    user = auth_service.get_user_by_id(user_id)
    payment_service = deps.get('payment_service')
    department_service = deps.get('department_service')
    notification_service = deps.get('notification_service')

    payments = payment_service.get_payments_by_tenant(user_id) if payment_service else []

    def _tenant_departments(user_obj, payment_list):
        ids = set()
        if user_obj and user_obj.department_id:
            ids.add(user_obj.department_id)
        for p in payment_list:
            if hasattr(p, "status") and p.status.value == PaymentStatus.APPROVED.value:
                ids.add(p.department_id)
        departments = []
        if department_service:
            for dep_id in ids:
                dept = department_service.get_department_by_id(dep_id)
                if dept:
                    departments.append(dept)
        return departments

    departments = _tenant_departments(user, payments)

    if not departments:
        flash("Debes tener un departamento asignado o un pago aprobado para crear reportes", "error")
        return redirect(url_for("tenant.dashboard"))
    
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        selected_department_id = request.form.get("department_id")

        department_id = selected_department_id or (departments[0].id if departments else None)
        
        report_service = deps.get('report_service')
        try:
            report = report_service.create_report(
                tenant_id=user_id,
                department_id=department_id,
                title=title,
                description=description
            )
            # Notificar a admins sobre nuevo reporte
            if notification_service and auth_service:
                admins = auth_service.user_repo.get_admins()
                for admin in admins:
                    notification_service.create(
                        user_id=admin.id,
                        title="Nuevo reporte",
                        message=f"{title}",
                        link=url_for("admin.reports_list", _external=False),
                        type="report_created"
                    )
            flash("Reporte creado correctamente", "success")
            return redirect(url_for("tenant.dashboard"))
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error al crear el reporte: {str(e)}", "error")
    
    return render_template("tenant/new_report.html")
