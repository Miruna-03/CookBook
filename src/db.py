import json
import sqlite3
import os
from data_json import load_json


def connect_db(db_name="recipes_clean2.db"):
    """Connect to SQLite database."""
    try:
        conn = sqlite3.connect(db_name)
        print(f"[INFO] Connected to DB: {db_name}")
        return conn
    except Exception as e:
        print(f"[ERROR] Cannot connect to DB: {e}")
        return None


def create_table(conn):
    """Create recipe table with your specified columns."""
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS recipe (
                cuisine TEXT,
                title TEXT,
                rating FLOAT,
                prep_time INTEGER,
                cook_time INTEGER,
                total_time INTEGER,
                description TEXT,
                nutrients TEXT,
                serves TEXT
            );
        """)
        conn.commit()
        print("[INFO] Table created successfully.")
    except Exception as e:
        print(f"[ERROR] Table creation failed: {e}")


def insert_one_recipe(conn, recipe):
    """Insert a single recipe into the DB."""
    try:
        # Extract only the fields you need
        cuisine = recipe.get("cuisine")
        title = recipe.get("title")
        rating = recipe.get("rating")
        prep_time = recipe.get("prep_time")
        cook_time = recipe.get("cook_time")
        total_time = recipe.get("total_time")
        description = recipe.get("description")
        nutrients = recipe.get("nutrients")  # This is a dictionary
        serves = recipe.get("serves")
        
        # Convert nutrients dict to JSON string
        nutrients_json = json.dumps(nutrients) if nutrients else None
        
        # Insert into database
        conn.execute(
            """
            INSERT INTO recipe 
            (cuisine, title, rating, prep_time, cook_time, total_time, 
             description, nutrients, serves)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cuisine, title, rating, prep_time, cook_time, total_time,
                description, nutrients_json, serves
            )
        )
        conn.commit()
        return True
        
    except Exception as e:
        print(f"[ERROR] Insert failed for '{recipe.get('title', 'Unknown')}': {e}")
        return False


def main():
    file_path = r"C:\Users\Mirunalini\OneDrive\Desktop\Securin_Assesment\src\US_recipes_null.json"

    data = load_json(file_path)

    if data is None:
        print("[ERROR] No data loaded.")
        return

    print(f"[INFO] Data type: {type(data)}")
    print(f"[INFO] Number of recipes found: {len(data)}")

    conn = connect_db()
    if conn is None:
        return

    create_table(conn)

    # CRITICAL FIX: Handle dictionary structure (not list!)
    if isinstance(data, dict):
        print(f"\n[INFO] Processing {len(data)} recipes from dictionary...")
        inserted_count = 0
        
        for key, recipe in data.items():
            print(f"Processing: {recipe.get('title', 'No Title')}")
            if insert_one_recipe(conn, recipe):
                inserted_count += 1
        
        print(f"\n[SUMMARY] Successfully inserted {inserted_count} recipes")
        
    elif isinstance(data, list):
        print(f"\n[INFO] Processing {len(data)} recipes from list...")
        for recipe in data:
            insert_one_recipe(conn, recipe)
    else:
        print("[ERROR] JSON format not supported.")

    # Verification
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM recipe")
    count = cursor.fetchone()[0]
    print(f"\n[VERIFY] Total records in database: {count}")
    
    if count > 0:
        cursor.execute("SELECT title, cuisine, rating FROM recipe LIMIT 5")
        print("\nFirst 5 recipes inserted:")
        for row in cursor.fetchall():
            print(f"  ✓ {row[0]} ({row[1]}) - Rating: {row[2]}")
    else:
        print("\n⚠️  WARNING: No records found in database!")

    conn.close()
    print("\n[INFO] Database connection closed.")
    print("[INFO] Check recipes_clean2.db with SQLite Viewer extension!")


if __name__ == "__main__":
    main()