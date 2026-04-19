import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB", "rh_agent"),
        user=os.getenv("POSTGRES_USER", "rh_user"),
        password=os.getenv("POSTGRES_PASSWORD", "rh_password_secret"),
        cursor_factory=psycopg2.extras.RealDictCursor
    )


def init_db():
    """Crée les tables si elles n'existent pas."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL DEFAULT 'employee',
            department VARCHAR(100),
            contract_type VARCHAR(50) DEFAULT 'CDI',
            hire_date DATE,
            manager_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id SERIAL PRIMARY KEY,
            employee_id INTEGER REFERENCES employees(id),
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Base de données initialisée.")


def get_employee_by_email(email: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees WHERE email = %s", (email,))
    employee = cur.fetchone()
    cur.close()
    conn.close()
    return employee


def get_employee_by_id(employee_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees WHERE id = %s", (employee_id,))
    employee = cur.fetchone()
    cur.close()
    conn.close()
    return employee


def save_message(employee_id: int, role: str, content: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_history (employee_id, role, content) VALUES (%s, %s, %s)",
        (employee_id, role, content)
    )
    conn.commit()
    cur.close()
    conn.close()


def get_history(employee_id: int, limit: int = 20):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT role, content, created_at
           FROM chat_history
           WHERE employee_id = %s
           ORDER BY created_at DESC
           LIMIT %s""",
        (employee_id, limit)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return list(reversed(rows))