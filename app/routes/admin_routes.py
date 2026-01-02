from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from .auth_routes import require_auth, require_role
from ..domain.enums import UserRole, PaymentStatus, ReportStatus, DepartmentStatus
from ..domain.entities import Department
from ..factories.user_factory import UserFactory

admin_bp = Blueprint("admin", __name__)


def get_services():
    """Helper para obtener servicios desde el contexto de la app"""
    from flask import current_app
    return current_app.config.get('deps', {})


def get_current_user_id():
    """Obtiene el ID del usuario actual desde la sesión"""
    return session.get('user_id')


@admin_bp.route("/dashboard")
@require_auth
@require_role(UserRole.ADMIN)
def dashboard():
    """Panel del administrador"""
    deps = get_services()
    
    payment_service = deps.get('payment_service')
    report_service = deps.get('report_service')
    
    pending_payments = []
    open_reports = []
    
    if payment_service:
        pending_payments = payment_service.get_pending_payments()
    
    if report_service:
        open_reports = report_service.get_open_reports()
    
    return render_template(
        "admin/dashboard.html",
        pending_payments=pending_payments,
        open_reports=open_reports
    )


@admin_bp.route("/payments")
@require_auth
@require_role(UserRole.ADMIN)
def payments_list():
    """Lista de todos los pagos"""
    deps = get_services()
    payment_service = deps.get('payment_service')
    
    status_filter = request.args.get('status')
    payments = []
    
    if payment_service:
        if status_filter:
            try:
                status = PaymentStatus(status_filter)
                payments = payment_service.get_payments_by_status(status)
            except ValueError:
                payments = payment_service.get_pending_payments()
        else:
            # Obtener todos los pagos pendientes por defecto
            payments = payment_service.get_pending_payments()
    
    return render_template("admin/payments.html", payments=payments)


@admin_bp.route("/payment/<payment_id>")
@require_auth
@require_role(UserRole.ADMIN)
def payment_detail(payment_id: str):
    """Vista detallada de un pago"""
    deps = get_services()
    payment_service = deps.get('payment_service')
    auth_service = deps.get('auth_service')
    department_service = deps.get('department_service')

    payment = payment_service.get_payment_by_id(payment_id) if payment_service else None
    if not payment:
        flash("Pago no encontrado", "error")
        return redirect(url_for("admin.payments_list"))

    tenant = auth_service.get_user_by_id(payment.tenant_id) if auth_service else None
    department = department_service.get_department_by_id(payment.department_id) if department_service else None

    return render_template(
        "admin/payment_detail.html",
        payment=payment,
        tenant=tenant,
        department=department
    )


@admin_bp.route("/payment/<payment_id>/approve", methods=["POST"])
@require_auth
@require_role(UserRole.ADMIN)
def approve_payment(payment_id: str):
    """Aprueba un pago"""
    user_id = get_current_user_id()
    deps = get_services()
    payment_service = deps.get('payment_service')
    auth_service = deps.get('auth_service')
    department_service = deps.get('department_service')
    
    try:
        payment = payment_service.get_payment_by_id(payment_id)
        if not payment:
            flash("Pago no encontrado", "error")
            return redirect(url_for("admin.payments_list"))
        if not payment.receipt_url:
            flash("No se puede aprobar un pago sin comprobante", "error")
            return redirect(url_for("admin.payment_detail", payment_id=payment_id))

        approved = payment_service.approve_payment(payment_id, user_id)
        if approved:
            # Asignar departamento al inquilino si no lo tiene
            if auth_service and department_service:
                tenant = auth_service.get_user_by_id(approved.tenant_id)
                if tenant and not tenant.department_id:
                    tenant.department_id = approved.department_id
                    auth_service.user_repo.update(tenant)
                    department_service.mark_as_occupied(approved.department_id)
            flash("Pago aprobado correctamente", "success")
        else:
            flash("Error al aprobar el pago", "error")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    
    return redirect(url_for("admin.payment_detail", payment_id=payment_id))


@admin_bp.route("/payment/<payment_id>/reject", methods=["POST"])
@require_auth
@require_role(UserRole.ADMIN)
def reject_payment(payment_id: str):
    """Rechaza un pago"""
    user_id = get_current_user_id()
    deps = get_services()
    payment_service = deps.get('payment_service')
    
    notes = request.form.get("notes", "")
    
    try:
        payment = payment_service.reject_payment(payment_id, user_id, notes)
        if payment:
            flash("Pago rechazado", "info")
        else:
            flash("Error al rechazar el pago", "error")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    
    return redirect(url_for("admin.payments_list"))


@admin_bp.route("/reports")
@require_auth
@require_role(UserRole.ADMIN)
def reports_list():
    """Lista de todos los reportes"""
    deps = get_services()
    report_service = deps.get('report_service')
    
    reports = []
    if report_service:
        reports = report_service.get_all_reports()
    
    return render_template("admin/reports.html", reports=reports)


@admin_bp.route("/report/<report_id>/resolve", methods=["POST"])
@require_auth
@require_role(UserRole.ADMIN)
def resolve_report(report_id: str):
    """Resuelve un reporte"""
    user_id = get_current_user_id()
    deps = get_services()
    report_service = deps.get('report_service')
    
    try:
        report = report_service.resolve_report(report_id, user_id)
        if report:
            flash("Reporte resuelto correctamente", "success")
        else:
            flash("Error al resolver el reporte", "error")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    
    return redirect(url_for("admin.reports_list"))


@admin_bp.route("/departments")
@require_auth
@require_role(UserRole.ADMIN)
def departments_list():
    """Lista de departamentos"""
    deps = get_services()
    department_service = deps.get('department_service')
    
    departments = []
    if department_service:
        departments = department_service.get_all_departments()
    
    return render_template("admin/departments.html", departments=departments)


@admin_bp.route("/department/new", methods=["GET", "POST"])
@require_auth
@require_role(UserRole.ADMIN)
def new_department():
    """Crear un nuevo departamento"""
    deps = get_services()
    department_service = deps.get('department_service')
    
    if request.method == "POST":
        try:
            image_url = None
            
            # Si se subió una imagen
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    file_content = file.read()
                    if len(file_content) > 0:
                        # Validar tamaño (máx 5MB para imágenes)
                        max_size = 5 * 1024 * 1024
                        if len(file_content) > max_size:
                            flash("La imagen es demasiado grande. Máximo 5MB", "error")
                            return render_template("admin/new_department.html")
                        
                        # Crear departamento primero (sin imagen)
                        department = Department(
                            id="",
                            title=request.form.get("title", "").strip(),
                            address=request.form.get("address", "").strip(),
                            price=float(request.form.get("price", 0)),
                            status=DepartmentStatus(request.form.get("status", DepartmentStatus.AVAILABLE.value)),
                            description=request.form.get("description", "").strip() or None,
                            rooms=int(request.form.get("rooms", 0)) if request.form.get("rooms") else None,
                            bathrooms=int(request.form.get("bathrooms", 0)) if request.form.get("bathrooms") else None,
                            area=float(request.form.get("area", 0)) if request.form.get("area") else None,
                            image_url=None
                        )
                        
                        department = department_service.create_department(department)
                        
                        # Subir imagen después de crear el departamento
                        try:
                            department = department_service.upload_department_image(
                                department_id=department.id,
                                file_content=file_content,
                                file_name=file.filename
                            )
                        except Exception as img_error:
                            flash(f"Departamento creado pero error al subir imagen: {str(img_error)}", "warning")
                    else:
                        # Usar URL si se proporcionó
                        image_url = request.form.get("image_url", "").strip() or None
                        department = Department(
                            id="",
                            title=request.form.get("title", "").strip(),
                            address=request.form.get("address", "").strip(),
                            price=float(request.form.get("price", 0)),
                            status=DepartmentStatus(request.form.get("status", DepartmentStatus.AVAILABLE.value)),
                            description=request.form.get("description", "").strip() or None,
                            rooms=int(request.form.get("rooms", 0)) if request.form.get("rooms") else None,
                            bathrooms=int(request.form.get("bathrooms", 0)) if request.form.get("bathrooms") else None,
                            area=float(request.form.get("area", 0)) if request.form.get("area") else None,
                            image_url=image_url
                        )
                        department = department_service.create_department(department)
                else:
                    # Usar URL si se proporcionó
                    image_url = request.form.get("image_url", "").strip() or None
                    department = Department(
                        id="",
                        title=request.form.get("title", "").strip(),
                        address=request.form.get("address", "").strip(),
                        price=float(request.form.get("price", 0)),
                        status=DepartmentStatus(request.form.get("status", DepartmentStatus.AVAILABLE.value)),
                        description=request.form.get("description", "").strip() or None,
                        rooms=int(request.form.get("rooms", 0)) if request.form.get("rooms") else None,
                        bathrooms=int(request.form.get("bathrooms", 0)) if request.form.get("bathrooms") else None,
                        area=float(request.form.get("area", 0)) if request.form.get("area") else None,
                        image_url=image_url
                    )
                    department = department_service.create_department(department)
            else:
                # Usar URL si se proporcionó
                image_url = request.form.get("image_url", "").strip() or None
                department = Department(
                    id="",
                    title=request.form.get("title", "").strip(),
                    address=request.form.get("address", "").strip(),
                    price=float(request.form.get("price", 0)),
                    status=DepartmentStatus(request.form.get("status", DepartmentStatus.AVAILABLE.value)),
                    description=request.form.get("description", "").strip() or None,
                    rooms=int(request.form.get("rooms", 0)) if request.form.get("rooms") else None,
                    bathrooms=int(request.form.get("bathrooms", 0)) if request.form.get("bathrooms") else None,
                    area=float(request.form.get("area", 0)) if request.form.get("area") else None,
                    image_url=image_url
                )
                department = department_service.create_department(department)
            
            flash("Departamento creado correctamente", "success")
            return redirect(url_for("admin.departments_list"))
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
    
    return render_template("admin/new_department.html")


@admin_bp.route("/department/<department_id>/edit", methods=["GET", "POST"])
@require_auth
@require_role(UserRole.ADMIN)
def edit_department(department_id: str):
    """Editar un departamento"""
    deps = get_services()
    department_service = deps.get('department_service')
    
    department = department_service.get_department_by_id(department_id)
    if not department:
        flash("Departamento no encontrado", "error")
        return redirect(url_for("admin.departments_list"))
    
    if request.method == "POST":
        try:
            department.title = request.form.get("title", "").strip()
            department.address = request.form.get("address", "").strip()
            department.price = float(request.form.get("price", 0))
            department.status = DepartmentStatus(request.form.get("status", DepartmentStatus.AVAILABLE.value))
            department.description = request.form.get("description", "").strip() or None
            department.rooms = int(request.form.get("rooms", 0)) if request.form.get("rooms") else None
            department.bathrooms = int(request.form.get("bathrooms", 0)) if request.form.get("bathrooms") else None
            department.area = float(request.form.get("area", 0)) if request.form.get("area") else None
            
            # Manejar imagen
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    file_content = file.read()
                    if len(file_content) > 0:
                        max_size = 5 * 1024 * 1024
                        if len(file_content) > max_size:
                            flash("La imagen es demasiado grande. Máximo 5MB", "error")
                            return render_template("admin/edit_department.html", department=department)
                        
                        try:
                            department = department_service.upload_department_image(
                                department_id=department_id,
                                file_content=file_content,
                                file_name=file.filename
                            )
                        except Exception as img_error:
                            flash(f"Error al subir imagen: {str(img_error)}", "warning")
                            # Continuar con la actualización sin cambiar la imagen
                            department.image_url = request.form.get("image_url", "").strip() or department.image_url
                    else:
                        department.image_url = request.form.get("image_url", "").strip() or department.image_url
                else:
                    department.image_url = request.form.get("image_url", "").strip() or department.image_url
            else:
                department.image_url = request.form.get("image_url", "").strip() or department.image_url
            
            department = department_service.update_department(department)
            flash("Departamento actualizado correctamente", "success")
            return redirect(url_for("admin.departments_list"))
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
    
    return render_template("admin/edit_department.html", department=department)


@admin_bp.route("/department/<department_id>/delete", methods=["POST"])
@require_auth
@require_role(UserRole.ADMIN)
def delete_department(department_id: str):
    """Eliminar un departamento"""
    deps = get_services()
    department_service = deps.get('department_service')
    
    try:
        success = department_service.delete_department(department_id)
        if success:
            flash("Departamento eliminado correctamente", "success")
        else:
            flash("Error al eliminar el departamento", "error")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
    
    return redirect(url_for("admin.departments_list"))


@admin_bp.route("/create-admin", methods=["GET", "POST"])
@require_auth
@require_role(UserRole.ADMIN)
def create_admin():
    """Crear un nuevo usuario administrador (solo para admins existentes)"""
    deps = get_services()
    auth_service = deps.get('auth_service')
    
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")
        full_name = request.form.get("full_name", "").strip()
        
        if not email or not password or not full_name:
            flash("Todos los campos son requeridos", "error")
            return render_template("admin/create_admin.html")
        
        if password != password_confirm:
            flash("Las contraseñas no coinciden", "error")
            return render_template("admin/create_admin.html")
        
        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres", "error")
            return render_template("admin/create_admin.html")
        
        try:
            user = auth_service.register(
                email=email,
                password=password,
                full_name=full_name,
                role=UserRole.ADMIN
            )
            flash(f"✅ Usuario administrador {email} creado exitosamente", "success")
            return redirect(url_for("admin.dashboard"))
        except ValueError as e:
            flash(str(e), "error")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
    
    return render_template("admin/create_admin.html")
