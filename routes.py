import datetime
from flask import render_template, request, redirect, url_for, flash, abort, session, jsonify, make_response
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, limiter
from models import User, Company, Department, Dashboard, UserRole
from forms import (
    LoginForm, UserForm, EditUserForm, ChangePasswordForm,
    CompanyForm, DepartmentForm, DashboardForm
)
from utils import (
    check_master_access, check_admin_access, check_company_access, 
    check_department_access, check_dashboard_access,
    get_accessible_companies, get_accessible_departments, get_accessible_dashboards,
    get_power_bi_iframe
)

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

# Error handlers
@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

# Authentication routes
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.is_locked:
            flash('Account is locked. Please contact an administrator.', 'danger')
            return render_template('login.html', form=form)
        
        if user and user.check_password(form.password.data):
            # Reset failed login attempts on successful login
            user.failed_login_attempts = 0
            user.last_login = datetime.datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            # Increment failed login attempts
            if user:
                user.failed_login_attempts += 1
                # Lock account after 5 failed attempts
                if user.failed_login_attempts >= 5:
                    user.is_locked = True
                    flash('Too many failed login attempts. Account has been locked.', 'danger')
                db.session.commit()
            
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    try:
        logout_user()
        db.session.commit()  # Assegura que todas as transações estejam finalizadas
        flash('You have been logged out.', 'success')
    except Exception as e:
        db.session.rollback()  # Faz rollback explícito em caso de erro
        print(f"Logout error: {str(e)}")
    return redirect(url_for('login'))

@app.route('/forgot-password')
def forgot_password():
    flash('Please contact the administrator to receive new access.', 'info')
    return redirect(url_for('login'))

# Dashboard routes
@app.route('/dashboard')
@app.route('/dashboard/department/<int:department_id>')
@login_required
def dashboard(department_id=None):
    if department_id:
        # Verificar se o usuário tem acesso ao departamento
        if not check_department_access(department_id):
            abort(403)
        # Filtrar dashboards apenas do departamento selecionado
        department = Department.query.get_or_404(department_id)
        
        # Garantir que apenas dashboards ativos sejam retornados
        dashboards = Dashboard.query.filter(
            Dashboard.department_id == department_id,
            Dashboard.is_active == True
        ).all()
        
        title = f"Department: {department.name}"
    else:
        # Todos os dashboards acessíveis
        dashboards = get_accessible_dashboards()
        title = "My Dashboards"
    
    # Passar o ID do departamento selecionado para o template
    return render_template('dashboard/index.html', 
                          dashboards=dashboards, 
                          title=title, 
                          selected_department_id=department_id)

@app.route('/dashboard/view/<int:dashboard_id>')
@login_required
def view_dashboard(dashboard_id):
    dashboard = Dashboard.query.get_or_404(dashboard_id)
    
    if not check_dashboard_access(dashboard_id):
        abort(403)
    
    iframe_html = get_power_bi_iframe(dashboard.power_bi_link)
    
    # Adicionando cabeçalhos de segurança para evitar visualização do código fonte
    response = make_response(render_template('dashboard/view.html', dashboard=dashboard, iframe_html=iframe_html))
    response.headers['Content-Security-Policy'] = "default-src 'self' https://*.powerbi.com; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; img-src 'self' data: https://*.powerbi.com; frame-src https://*.powerbi.com"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    
    return response

# Company routes (Master only)
@app.route('/companies')
@login_required
def companies():
    check_master_access()
    companies = Company.query.all()
    return render_template('admin/companies.html', companies=companies)

@app.route('/companies/add', methods=['GET', 'POST'])
@login_required
def add_company():
    check_master_access()
    
    form = CompanyForm()
    if form.validate_on_submit():
        company = Company(
            name=form.name.data,
            description=form.description.data,
            is_active=form.is_active.data
        )
        db.session.add(company)
        db.session.commit()
        flash('Company added successfully.', 'success')
        return redirect(url_for('companies'))
    
    return render_template('admin/company_form.html', form=form, title='Add Company')

@app.route('/companies/edit/<int:company_id>', methods=['GET', 'POST'])
@login_required
def edit_company(company_id):
    check_master_access()
    
    company = Company.query.get_or_404(company_id)
    form = CompanyForm(obj=company)
    
    if form.validate_on_submit():
        company.name = form.name.data
        company.description = form.description.data
        company.is_active = form.is_active.data
        db.session.commit()
        flash('Company updated successfully.', 'success')
        return redirect(url_for('companies'))
    
    return render_template('admin/company_form.html', form=form, company=company, title='Edit Company')

@app.route('/companies/delete/<int:company_id>', methods=['POST'])
@login_required
def delete_company(company_id):
    check_master_access()
    
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()
    flash('Company deleted successfully.', 'success')
    return redirect(url_for('companies'))

# Department routes (Master and Admin)
@app.route('/departments')
@login_required
def departments():
    check_admin_access()
    
    if current_user.is_master():
        departments = Department.query.all()
    else:  # Admin
        departments = Department.query.filter_by(company_id=current_user.company_id).all()
    
    return render_template('admin/departments.html', departments=departments)

@app.route('/departments/add', methods=['GET', 'POST'])
@login_required
def add_department():
    check_admin_access()
    
    form = DepartmentForm()
    
    # Set company choices based on user role
    if current_user.is_master():
        form.company_id.choices = [(c.id, c.name) for c in Company.query.all()]
    else:  # Admin
        form.company_id.choices = [(current_user.company_id, current_user.company.name)]
        form.company_id.data = current_user.company_id
    
    if form.validate_on_submit():
        # Validate access to the selected company
        if not check_company_access(form.company_id.data):
            abort(403)
        
        department = Department(
            name=form.name.data,
            description=form.description.data,
            is_active=form.is_active.data,
            company_id=form.company_id.data
        )
        db.session.add(department)
        db.session.flush()  # Para obter o ID do departamento antes do commit
        
        # Atribuir automaticamente o novo departamento a todos administradores da mesma empresa
        admin_users = User.query.filter(
            (User.company_id == form.company_id.data) & 
            ((User.role == UserRole.ADMIN) | (User.role == UserRole.MASTER))
        ).all()
        
        for admin_user in admin_users:
            admin_user.departments.append(department)
            
        db.session.commit()
        flash('Department added successfully.', 'success')
        return redirect(url_for('departments'))
    
    return render_template('admin/department_form.html', form=form, title='Add Department')

@app.route('/departments/edit/<int:department_id>', methods=['GET', 'POST'])
@login_required
def edit_department(department_id):
    check_admin_access()
    
    department = Department.query.get_or_404(department_id)
    
    # Check if user has access to this department
    if not check_department_access(department_id):
        abort(403)
    
    form = DepartmentForm(obj=department)
    
    # Set company choices based on user role
    if current_user.is_master():
        form.company_id.choices = [(c.id, c.name) for c in Company.query.all()]
    else:  # Admin
        form.company_id.choices = [(current_user.company_id, current_user.company.name)]
        form.company_id.data = current_user.company_id
    
    if form.validate_on_submit():
        # Validate access to the selected company
        if not check_company_access(form.company_id.data):
            abort(403)
        
        # Verificar se a empresa do departamento está sendo alterada
        old_company_id = department.company_id
        new_company_id = form.company_id.data
        
        department.name = form.name.data
        department.description = form.description.data
        department.is_active = form.is_active.data
        department.company_id = new_company_id
        
        # Se a empresa foi alterada, precisamos atualizar as permissões dos usuários
        if old_company_id != new_company_id:
            # Remover o departamento dos usuários da empresa antiga
            old_users = User.query.filter_by(company_id=old_company_id).all()
            for user in old_users:
                if department in user.departments:
                    user.departments.remove(department)
            
            # Adicionar o departamento para os administradores da nova empresa
            new_admin_users = User.query.filter(
                (User.company_id == new_company_id) & 
                ((User.role == UserRole.ADMIN) | (User.role == UserRole.MASTER))
            ).all()
            for admin_user in new_admin_users:
                if department not in admin_user.departments:
                    admin_user.departments.append(department)
        
        db.session.commit()
        flash('Department updated successfully.', 'success')
        return redirect(url_for('departments'))
    
    return render_template('admin/department_form.html', form=form, department=department, title='Edit Department')

@app.route('/departments/delete/<int:department_id>', methods=['POST'])
@login_required
def delete_department(department_id):
    check_admin_access()
    
    department = Department.query.get_or_404(department_id)
    
    # Check if user has access to this department
    if not check_department_access(department_id):
        abort(403)
    
    db.session.delete(department)
    db.session.commit()
    flash('Department deleted successfully.', 'success')
    return redirect(url_for('departments'))

# Dashboard management routes (Master and Admin)
@app.route('/dashboards/manage')
@login_required
def manage_dashboards():
    check_admin_access()
    
    if current_user.is_master():
        dashboards = Dashboard.query.all()
    else:  # Admin
        department_ids = [d.id for d in Department.query.filter_by(company_id=current_user.company_id).all()]
        dashboards = Dashboard.query.filter(Dashboard.department_id.in_(department_ids)).all()
    
    return render_template('admin/dashboards.html', dashboards=dashboards)

@app.route('/dashboards/add', methods=['GET', 'POST'])
@login_required
def add_dashboard():
    check_admin_access()
    
    form = DashboardForm()
    
    # Set department choices based on user role
    if current_user.is_master():
        departments = Department.query.all()
    else:  # Admin
        departments = Department.query.filter_by(company_id=current_user.company_id).all()
    
    form.department_id.choices = [(d.id, d.name) for d in departments]
    
    if form.validate_on_submit():
        # Validate access to the selected department
        if not check_department_access(form.department_id.data):
            abort(403)
        
        dashboard = Dashboard(
            name=form.name.data,
            description=form.description.data,
            power_bi_link=form.power_bi_link.data,
            is_active=form.is_active.data,
            department_id=form.department_id.data
        )
        db.session.add(dashboard)
        db.session.commit()
        flash('Dashboard added successfully.', 'success')
        return redirect(url_for('manage_dashboards'))
    
    return render_template('admin/dashboard_form.html', form=form, title='Add Dashboard')

@app.route('/dashboards/edit/<int:dashboard_id>', methods=['GET', 'POST'])
@login_required
def edit_dashboard(dashboard_id):
    check_admin_access()
    
    dashboard = Dashboard.query.get_or_404(dashboard_id)
    
    # Check if user has access to this dashboard's department
    if not check_department_access(dashboard.department_id):
        abort(403)
    
    form = DashboardForm(obj=dashboard)
    
    # Set department choices based on user role
    if current_user.is_master():
        departments = Department.query.all()
    else:  # Admin
        departments = Department.query.filter_by(company_id=current_user.company_id).all()
    
    form.department_id.choices = [(d.id, d.name) for d in departments]
    
    if form.validate_on_submit():
        # Validate access to the selected department
        if not check_department_access(form.department_id.data):
            abort(403)
        
        dashboard.name = form.name.data
        dashboard.description = form.description.data
        dashboard.power_bi_link = form.power_bi_link.data
        dashboard.is_active = form.is_active.data
        dashboard.department_id = form.department_id.data
        db.session.commit()
        flash('Dashboard updated successfully.', 'success')
        return redirect(url_for('manage_dashboards'))
    
    return render_template('admin/dashboard_form.html', form=form, dashboard=dashboard, title='Edit Dashboard')

@app.route('/dashboards/delete/<int:dashboard_id>', methods=['POST'])
@login_required
def delete_dashboard(dashboard_id):
    check_admin_access()
    
    dashboard = Dashboard.query.get_or_404(dashboard_id)
    
    # Check if user has access to this dashboard's department
    if not check_department_access(dashboard.department_id):
        abort(403)
    
    db.session.delete(dashboard)
    db.session.commit()
    flash('Dashboard deleted successfully.', 'success')
    return redirect(url_for('manage_dashboards'))

# User management routes
@app.route('/users')
@login_required
def users():
    check_admin_access()
    
    if current_user.is_master():
        users = User.query.all()
    else:  # Admin
        users = User.query.filter_by(company_id=current_user.company_id).all()
    
    return render_template('admin/users.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    check_admin_access()
    
    form = UserForm()
    
    # Set company and department choices based on user role
    if current_user.is_master():
        # Masters can assign to any company and role
        form.company_id.choices = [(c.id, c.name) for c in Company.query.all()]
        form.role.choices = [
            (UserRole.MASTER, 'Master'),
            (UserRole.ADMIN, 'Administrator'),
            (UserRole.USER, 'User')
        ]
        
        # Only populate departments when company is selected (handled in JS)
        if form.company_id.data:
            departments = Department.query.filter_by(company_id=form.company_id.data).all()
            form.department_ids.choices = [(d.id, d.name) for d in departments]
        else:
            form.department_ids.choices = []
    else:  # Admin
        # Admins can only assign to their company and not as masters
        form.company_id.choices = [(current_user.company_id, current_user.company.name)]
        form.company_id.data = current_user.company_id
        form.role.choices = [
            (UserRole.ADMIN, 'Administrator'),
            (UserRole.USER, 'User')
        ]
        
        # Admins can only assign to their company's departments
        departments = Department.query.filter_by(company_id=current_user.company_id).all()
        form.department_ids.choices = [(d.id, d.name) for d in departments]
    
    if form.validate_on_submit():
        # Validate company access
        if not check_company_access(form.company_id.data):
            abort(403)
        
        # Validate department access (somente se houver departamentos selecionados e for usuário comum)
        if form.department_ids.data and form.role.data == UserRole.USER:
            for dept_id in form.department_ids.data:
                if not check_department_access(dept_id):
                    abort(403)
        
        # Validate role restrictions
        if not current_user.is_master() and form.role.data == UserRole.MASTER:
            abort(403)
        
        # Create the new user
        user = User(
            name=form.name.data,
            email=form.email.data,
            role=form.role.data,
            company_id=form.company_id.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.flush()  # Flush to get the user ID for department association
        
        # Associate departments based on role
        # Administradores têm acesso a todos os departamentos da empresa
        if form.role.data == UserRole.ADMIN:
            # Adicionar todos os departamentos da empresa ao usuário admin
            departments = Department.query.filter_by(company_id=form.company_id.data).all()
            for dept in departments:
                user.departments.append(dept)
        # Usuários comuns só têm acesso aos departamentos selecionados
        elif form.role.data == UserRole.USER and form.department_ids.data:
            for dept_id in form.department_ids.data:
                department = Department.query.get(dept_id)
                if department and department.company_id == user.company_id:
                    user.departments.append(department)
        
        db.session.commit()
        flash('User added successfully.', 'success')
        return redirect(url_for('users'))
    
    return render_template('admin/user_form.html', form=form, title='Add User')

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    check_admin_access()
    
    user = User.query.get_or_404(user_id)
    
    # Check if current user has permission to edit this user
    if not current_user.is_master() and (user.company_id != current_user.company_id or user.is_master()):
        abort(403)
    
    form = EditUserForm(user.email, obj=user)
    
    # Set company and department choices based on user role
    if current_user.is_master():
        # Masters can assign to any company and role
        form.company_id.choices = [(c.id, c.name) for c in Company.query.all()]
        form.role.choices = [
            (UserRole.MASTER, 'Master'),
            (UserRole.ADMIN, 'Administrator'),
            (UserRole.USER, 'User')
        ]
        
        # Only populate departments when company is selected (handled in JS)
        if form.company_id.data:
            departments = Department.query.filter_by(company_id=form.company_id.data).all()
            form.department_ids.choices = [(d.id, d.name) for d in departments]
            form.department_ids.data = [d.id for d in user.departments]
    else:  # Admin
        # Admins can only assign to their company and not as masters
        form.company_id.choices = [(current_user.company_id, current_user.company.name)]
        form.company_id.data = current_user.company_id
        form.role.choices = [
            (UserRole.ADMIN, 'Administrator'),
            (UserRole.USER, 'User')
        ]
        
        # Admins can only assign to their company's departments
        departments = Department.query.filter_by(company_id=current_user.company_id).all()
        form.department_ids.choices = [(d.id, d.name) for d in departments]
        form.department_ids.data = [d.id for d in user.departments]
    
    if form.validate_on_submit():
        # Validate company access
        if not check_company_access(form.company_id.data):
            abort(403)
        
        # Validate department access (somente se houver departamentos selecionados)
        if form.department_ids.data is not None:
            for dept_id in form.department_ids.data:
                if not check_department_access(dept_id):
                    abort(403)
        
        # Validate role restrictions
        if not current_user.is_master() and form.role.data == UserRole.MASTER:
            abort(403)
        
        # Update user data
        user.name = form.name.data
        user.email = form.email.data
        user.role = form.role.data
        user.company_id = form.company_id.data
        
        # Atualizar senha se foi fornecida (apenas para Master ou Admin)
        if form.password.data and (user.is_master() or user.is_admin()):
            user.set_password(form.password.data)
        
        # Update department associations based on role
        user.departments = []
        
        # Administradores têm acesso a todos os departamentos da empresa
        if form.role.data == UserRole.ADMIN:
            # Adicionar todos os departamentos da empresa ao usuário admin
            departments = Department.query.filter_by(company_id=form.company_id.data).all()
            for dept in departments:
                user.departments.append(dept)
        # Usuários comuns só têm acesso aos departamentos selecionados
        elif form.role.data == UserRole.USER and form.department_ids.data:
            for dept_id in form.department_ids.data:
                department = Department.query.get(dept_id)
                if department and department.company_id == user.company_id:
                    user.departments.append(department)
        
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('users'))
    
    return render_template('admin/user_form.html', form=form, user=user, title='Edit User')

@app.route('/users/reset-password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def reset_user_password(user_id):
    check_admin_access()
    
    user = User.query.get_or_404(user_id)
    
    # Check if current user has permission to edit this user
    if not current_user.is_master() and (user.company_id != current_user.company_id or user.is_master()):
        abort(403)
    
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        user.is_locked = False  # Unlock account if it was locked
        user.failed_login_attempts = 0  # Reset failed attempts
        db.session.commit()
        flash('Password reset successfully.', 'success')
        return redirect(url_for('users'))
    
    return render_template('admin/user_password_reset.html', form=form, user=user)

@app.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    check_admin_access()
    
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('users'))
    
    # Check if current user has permission to delete this user
    if not current_user.is_master() and (user.company_id != current_user.company_id or user.is_master()):
        abort(403)
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('users'))

# API Routes
@app.route('/api/departments')
@login_required
def api_departments():
    company_id = request.args.get('company_id', type=int)
    if not company_id:
        return jsonify([])
        
    # Check if user has access to this company
    if not check_company_access(company_id):
        return jsonify([])
        
    departments = Department.query.filter_by(company_id=company_id, is_active=True).all()
    return jsonify([{"id": dept.id, "name": dept.name} for dept in departments])
