"""
Migration script to add session_id column to quiz_attempts table.
This allows anonymous users to have separate quiz result histories.
"""
from app import create_app, db
import sqlite3
import os

app = create_app()

with app.app_context():
    # Get the database URI from Flask config
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    # Extract the database path (remove 'sqlite:///' prefix)
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
    else:
        db_path = db_uri.replace('sqlite://', '')
    
    print(f"Checking database at: {db_path}")
    
    if not os.path.exists(db_path):
        print("Database doesn't exist. Creating new database...")
        db.create_all()
        print("Database created with correct schema!")
    else:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check if session_id column exists
            cursor.execute("PRAGMA table_info(quiz_attempts)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'session_id' not in columns:
                print("Adding session_id column to quiz_attempts table...")
                cursor.execute("ALTER TABLE quiz_attempts ADD COLUMN session_id VARCHAR(255)")
                # Create index for better query performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_quiz_attempts_session_id ON quiz_attempts(session_id)")
                conn.commit()
                print("Successfully added session_id column and index!")
            else:
                print("session_id column already exists!")
                
        except sqlite3.OperationalError as e:
            if "no such table" in str(e).lower():
                print("Table doesn't exist. Creating all tables...")
                conn.close()
                db.create_all()
                print("Tables created!")
            else:
                raise e
        finally:
            conn.close()
    
    # Verify schema matches models
    db.create_all()
    print("\nMigration complete! Your database is ready.")
    print("Note: Existing anonymous quiz attempts will have session_id=NULL")
    print("New anonymous attempts will have unique session_ids.")