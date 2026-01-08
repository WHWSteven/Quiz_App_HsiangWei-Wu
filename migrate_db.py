"""
Migration script to add user_id column to quiz_attempts table.
This fixes the "table quiz_attempts has no column named user_id" error.
"""
from app import create_app, db
import sqlite3
import os

app = create_app()

with app.app_context():
    db_path = 'instance/quiz.db'
    
    if not os.path.exists(db_path):
        print("Database doesn't exist. Creating new database...")
        db.create_all()
        print("Database created with correct schema!")
    else:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check if user_id column exists
            cursor.execute("PRAGMA table_info(quiz_attempts)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'user_id' not in columns:
                print("Adding user_id column to quiz_attempts table...")
                cursor.execute("ALTER TABLE quiz_attempts ADD COLUMN user_id INTEGER")
                conn.commit()
                print("Successfully added user_id column!")
            else:
                print("user_id column already exists!")
                
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
