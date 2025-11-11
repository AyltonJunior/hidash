import re
from flask import abort, flash
from flask_login import current_user
from models import User, Company, Department, Dashboard, UserRole
from app import db

def check_master_access():
    """Check if user is a master, otherwise abort with 403"""
    if not current_user.is_authenticated or not current_user.is_master():
        abort(403)

def check_admin_access():
    """Check if user is a master or admin, otherwise abort with 403"""
    if not current_user.is_authenticated or (not current_user.is_master() and not current_user.is_admin()):
        abort(403)

def check_company_access(company_id):
    """Check if user has access to the company"""
    if current_user.is_master():
        return True
    if current_user.is_admin() and current_user.company_id == company_id:
        return True
    return False

def check_department_access(department_id):
    """Check if user has access to the department"""
    department = Department.query.get(department_id)
    if not department:
        return False
    
    if current_user.is_master():
        return True
    if current_user.is_admin() and current_user.company_id == department.company_id:
        return True
    
    # Verificar se o usuário comum tem este departamento associado
    if current_user.is_common_user():
        for user_dept in current_user.departments:
            if user_dept.id == department_id:
                return True
    
    return False

def check_dashboard_access(dashboard_id):
    """Check if user has access to the dashboard"""
    dashboard = Dashboard.query.get(dashboard_id)
    if not dashboard:
        return False
    
    if current_user.is_master():
        return True
    
    if current_user.is_admin() and current_user.company_id == dashboard.department.company_id:
        return True
    
    # Check if user is in the department that has this dashboard
    user_department_ids = [d.id for d in current_user.departments]
    if dashboard.department_id in user_department_ids:
        return True
    
    return False

def get_accessible_companies():
    """Get companies accessible to the current user"""
    if current_user.is_master():
        return Company.query.all()
    elif current_user.is_admin():
        return [current_user.company] if current_user.company else []
    return []

def get_accessible_departments():
    """Get departments accessible to the current user"""
    if current_user.is_master():
        return Department.query.all()
    
    if current_user.is_admin():
        return Department.query.filter_by(company_id=current_user.company_id).all()
    
    return current_user.departments

def get_accessible_dashboards():
    """Get dashboards accessible to the current user"""
    if current_user.is_master():
        return Dashboard.query.all()
    
    if current_user.is_admin():
        department_ids = [d.id for d in Department.query.filter_by(company_id=current_user.company_id).all()]
        return Dashboard.query.filter(Dashboard.department_id.in_(department_ids)).all()
    
    # For regular users, return dashboards from their departments
    department_ids = [d.id for d in current_user.departments]
    return Dashboard.query.filter(Dashboard.department_id.in_(department_ids)).all()

def get_power_bi_iframe(power_bi_link):
    """Generate secure iframe HTML for Power BI dashboard"""
    # Aceitar qualquer URL válido do Power BI
    # Exemplo: https://app.powerbi.com/view?r=eyJrIjoiYTdiNmQxNWEtMzQ3YS00OTU0LTkwNWQtM2RjMGM5ZDA3YmYxIiwidCI6IjQwNmQxM2ZmLTZmN2UtNGQ0Ni05NjUxLTU4NGJjMDE0ZWQxNyJ9
    
    # Create a secure iframe with proper attributes for fullscreen
    iframe_html = f"""
    <iframe 
        title="Power BI Dashboard" 
        width="100%" 
        height="100%" 
        src="{power_bi_link}" 
        frameborder="0" 
        allowFullScreen="true" 
        sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
        style="pointer-events: auto;"
        oncontextmenu="return false;"
    >
    </iframe>
    <script>
        // Prevent right-click
        document.addEventListener('contextmenu', function(e) {{
            e.preventDefault();
        }});
        
        // Prevent keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            // Prevent F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+U
            if (
                e.keyCode === 123 || 
                (e.ctrlKey && e.shiftKey && e.keyCode === 73) || 
                (e.ctrlKey && e.shiftKey && e.keyCode === 74) || 
                (e.ctrlKey && e.keyCode === 85)
            ) {{
                e.preventDefault();
            }}
        }});
    </script>
    """
    return iframe_html
