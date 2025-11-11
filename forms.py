from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp, Optional
from models import User, UserRole
from config import Config

# Password validation regex
password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$'
password_message = 'Password must contain at least 8 characters, including uppercase, lowercase, number and special character.'

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Regexp(password_regex, message=password_message)
    ])
    confirm_password = PasswordField(
        'Confirm Password', 
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    role = SelectField('Role', choices=[
        (UserRole.MASTER, 'Master'),
        (UserRole.ADMIN, 'Administrator'),
        (UserRole.USER, 'User')
    ])
    company_id = SelectField('Company', coerce=int)
    department_ids = SelectMultipleField('Departments', coerce=int)
    
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        # Initialize with empty choices to prevent NoneType error
        if not self.department_ids.choices:
            self.department_ids.choices = []
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class EditUserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[
        (UserRole.MASTER, 'Master'),
        (UserRole.ADMIN, 'Administrator'),
        (UserRole.USER, 'User')
    ])
    company_id = SelectField('Company', coerce=int)
    department_ids = SelectMultipleField('Departments', coerce=int)
    
    # Campos de senha opcional para edição
    password = PasswordField('New Password', validators=[
        Optional(),
        Regexp(password_regex, message=password_message)
    ])
    confirm_password = PasswordField(
        'Confirm New Password', 
        validators=[EqualTo('password', message='Passwords must match')]
    )
    
    def __init__(self, original_email, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
        # Initialize with empty choices to prevent NoneType error
        if not self.department_ids.choices:
            self.department_ids.choices = []
        
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered.')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Regexp(password_regex, message=password_message)
    ])
    confirm_password = PasswordField(
        'Confirm New Password', 
        validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')]
    )

class CompanyForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description')
    is_active = BooleanField('Active', default=True)

class DepartmentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description')
    is_active = BooleanField('Active', default=True)
    company_id = SelectField('Company', coerce=int)

class DashboardForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Length(max=100)])
    power_bi_link = StringField('Power BI Link', validators=[DataRequired(), Length(min=5, max=500)])
    is_active = BooleanField('Active', default=True)
    department_id = SelectField('Department', coerce=int)
    
    def __init__(self, *args, **kwargs):
        super(DashboardForm, self).__init__(*args, **kwargs)
        # Initialize with empty choices to prevent NoneType error
        if not self.department_id.choices:
            self.department_id.choices = []
