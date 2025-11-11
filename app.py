import os
import logging
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.environ.get("SESSION_SECRET", "hidash_secure_key")
app.permanent_session_lifetime = timedelta(hours=12)

# Detectar ambiente Vercel
IS_VERCEL = os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV')

# ProxyFix apenas se não estiver na Vercel (a Vercel já faz proxy reverso)
if not IS_VERCEL:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize database with improved connection handling for serverless
# Ajustar pool size para ambiente serverless (menos conexões simultâneas)
pool_size = 1 if IS_VERCEL else 10
max_overflow = 0 if IS_VERCEL else 15

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 280,
    "pool_size": pool_size,
    "max_overflow": max_overflow,
    "connect_args": {
        "connect_timeout": 10
    }
}
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'danger'

# Initialize rate limiter for brute force protection
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Import models here to avoid circular imports
# Em ambiente serverless, não criar tabelas automaticamente (usar migrations)
with app.app_context():
    from models import User, Company, Department, Dashboard
    # Apenas criar tabelas se não estiver em produção ou se DATABASE_URL estiver definido
    if not IS_VERCEL or os.environ.get('DATABASE_URL'):
        try:
            db.create_all()
            logging.info("Database tables created/verified")
        except Exception as e:
            logging.warning(f"Database initialization warning: {str(e)}")

# Import routes after database initialization
from routes import *
