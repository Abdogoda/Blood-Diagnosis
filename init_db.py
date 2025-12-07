"""
Database initialization script.
Creates all tables in the database.
"""
from app.database import Base, engine

def init_db():
    """Drop all existing tables and create fresh ones."""
    print("Dropping existing database tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
