import os
import random
import string
from app import app, db
from models import User, Company, Department, Dashboard, UserRole
from werkzeug.security import generate_password_hash

def random_password(length=12):
    """Generate a random strong password"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def create_initial_data():
    """Create initial data for the application"""
    with app.app_context():
        # Check if there's already a master user
        if User.query.filter_by(role=UserRole.MASTER).first():
            print("Database already initialized with a master user.")
            return
        
        # Create master user
        master_password = os.environ.get('MASTER_PASSWORD', 'Master@2023')
        master = User(
            name='System Administrator',
            email='admin@hidash.com',
            role=UserRole.MASTER,
            password_hash=generate_password_hash(master_password)
        )
        
        db.session.add(master)
        db.session.commit()
        
        print("Initial master user created:")
        print(f"Email: admin@hidash.com")
        print(f"Password: {master_password}")

if __name__ == "__main__":
    create_initial_data()
