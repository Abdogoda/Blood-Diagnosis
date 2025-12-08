"""
Create admin user for the Blood Diagnosis System.
Run this script to create an initial admin user.
"""
from app.database import SessionLocal, User
from app.services import hash_password
import getpass

def create_admin():
    """Create an admin user."""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("Create Admin User for Blood Diagnosis System")
        print("=" * 60)
        
        # Get admin details
        username = input("\nEnter admin username: ").strip()
        
        # Check if username exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"\n✗ Error: Username '{username}' already exists!")
            return
        
        email = input("Enter admin email: ").strip()
        
        # Check if email exists
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            print(f"\n✗ Error: Email '{email}' already exists!")
            return
        
        fname = input("Enter first name: ").strip()
        lname = input("Enter last name: ").strip()
        
        # Get password securely
        while True:
            password = getpass.getpass("Enter password (min 8 characters): ")
            if len(password) < 8:
                print("✗ Password must be at least 8 characters long!")
                continue
            
            confirm_password = getpass.getpass("Confirm password: ")
            if password != confirm_password:
                print("✗ Passwords do not match!")
                continue
            
            break
        
        # Create admin user
        admin_user = User(
            username=username,
            email=email,
            password=hash_password(password),
            fname=fname,
            lname=lname,
            role="admin"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("\n" + "=" * 60)
        print("✓ Admin user created successfully!")
        print("=" * 60)
        print(f"User ID: {admin_user.id}")
        print(f"Username: {admin_user.username}")
        print(f"Email: {admin_user.email}")
        print(f"Role: {admin_user.role}")
        print(f"Created at: {admin_user.created_at}")
        print("\nYou can now login with these credentials.")
        
    except Exception as e:
        print(f"\n✗ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
