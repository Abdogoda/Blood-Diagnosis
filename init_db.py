"""
Database initialization script.
Creates all tables in the database.
"""
from app.database import Base, engine
from app.database import SessionLocal, User, Model
from app.services.auth_service import hash_password
import sys

def init_db():
    """Drop all existing tables and create fresh ones."""
    print("Dropping existing database tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    run_all_seeders()

def run_all_seeders():
    """Run all seeders."""
    print("\nRunning Database Seeders...")
    print("=" * 60)
    
    try:
        print("\n[1/2] Seeding Admin User...")
        seed_admin()
        
        print("\n[2/2] Seeding AI Models...")
        seed_models()
        
        print("✓ ALL SEEDERS COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"\n✗ Error running seeders: {str(e)}")
        sys.exit(1)

def seed_admin():
    """Create default admin user."""
    db = SessionLocal()
    
    try:
        existing_admin = db.query(User).filter(User.username == "admin", User.email == "admin@gmail.com").first()
        if existing_admin:
            print("\n✓ Admin user already exists!")
            print(f"   Username: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            return
        
        admin = User(
            username="admin",
            password=hash_password("123456789"),  # Default password
            fname="Admin",
            lname="User",
            gender="male",
            email="admin@gmail.com",
            role="admin",
            phone="1234567890",
            address="System Administrator",
            is_active=1
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("\nDefault Admin Credentials:")
        print("  Username: admin")
        print("  Password: 123456789")
        
    except Exception as e:
        print(f"\n✗ Error creating admin user: {str(e)}")
        db.rollback()
    finally:
        db.close()


def seed_models():
    """Create default AI models."""
    db = SessionLocal()
    
    try:
        models_data = [
            {
                "name": "CBC Anemia Detection",
                "accuracy": 95.0,
                "tests_count": 0
            },
            {
                "name": "Blood Cell Image Classification",
                "accuracy": 92.30,
                "tests_count": 0
            }
        ]
        
        created_count = 0
        existing_count = 0
        
        for model_data in models_data:
            existing_model = db.query(Model).filter(Model.name == model_data["name"]).first()
            
            if existing_model:
                print(f"\n✓ Model already exists: {existing_model.name}")
                existing_count += 1
            else:
                # Create new model
                new_model = Model(
                    name=model_data["name"],
                    accuracy=model_data["accuracy"],
                    tests_count=model_data["tests_count"]
                )
                
                db.add(new_model)
                db.commit()
                db.refresh(new_model)
                
                created_count += 1
        
    except Exception as e:
        print(f"\n✗ Error seeding models: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
