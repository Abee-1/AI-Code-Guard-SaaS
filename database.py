import sqlite3

def init_db():
    conn = sqlite3.connect("saas.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        api_key TEXT UNIQUE NOT NULL,
        plan_tier TEXT DEFAULT 'Free'
    )
    """)
    
    try:
        # Seed the database with commercial enterprise credentials
        cursor.executemany("""
        INSERT INTO clients (company_name, username, password, api_key, plan_tier) VALUES (?, ?, ?, ?, ?)
        """, [
            ("Alpha Startup", "alpha_dev", "startuppass123", "dev-token-company-alpha-12345", "Free"),
            ("Enterprise Corp", "enterprise_admin", "securecorp99", "prod-token-enterprise-99887", "Premium")
        ])
        conn.commit()
        print("[✓] Database upgraded with user login credentials!")
    except sqlite3.IntegrityError:
        print("[✓] Database loaded successfully.")
    
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect("saas.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT company_name, api_key, plan_tier 
        FROM clients 
        WHERE username = ? AND password = ?
    """, (username, password))
    result = cursor.fetchone()
    conn.close()
    return result  # Returns (company_name, api_key, plan_tier) or None

def verify_key_in_db(provided_key: str) -> bool:
    conn = sqlite3.connect("saas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM clients WHERE api_key = ?", (provided_key,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

if __name__ == "__main__":
    init_db()
