"""
Script d'initialisation : crée les tables et insère les comptes de démo.
Exécuté automatiquement au démarrage du conteneur backend.
"""
import time
import psycopg2
from database import init_db, get_connection
from auth import hash_password


DEMO_EMPLOYEES = [
    {
        "email": "alice@demo.fr",
        "password": "demo123",
        "full_name": "Alice Martin",
        "role": "employee",
        "department": "Marketing",
        "contract_type": "CDI",
        "hire_date": "2022-03-15",
        "manager_name": "Bob Dupont"
    },
    {
        "email": "bob@demo.fr",
        "password": "demo123",
        "full_name": "Bob Dupont",
        "role": "manager",
        "department": "Marketing",
        "contract_type": "CDI",
        "hire_date": "2019-09-01",
        "manager_name": "Sarah RH"
    },
    {
        "email": "sarah@demo.fr",
        "password": "demo123",
        "full_name": "Sarah Lambert",
        "role": "rh",
        "department": "Ressources Humaines",
        "contract_type": "CDI",
        "hire_date": "2017-01-10",
        "manager_name": None
    }
]


def wait_for_db(retries=10, delay=3):
    """Attend que PostgreSQL soit prêt."""
    for i in range(retries):
        try:
            conn = get_connection()
            conn.close()
            print("PostgreSQL est prêt.")
            return True
        except psycopg2.OperationalError:
            print(f"Attente PostgreSQL... ({i+1}/{retries})")
            time.sleep(delay)
    return False


def seed():
    if not wait_for_db():
        print("Impossible de se connecter à PostgreSQL.")
        return

    init_db()

    conn = get_connection()
    cur = conn.cursor()

    for emp in DEMO_EMPLOYEES:
        cur.execute("SELECT id FROM employees WHERE email = %s", (emp["email"],))
        exists = cur.fetchone()
        if not exists:
            cur.execute("""
                INSERT INTO employees
                    (email, password_hash, full_name, role, department, contract_type, hire_date, manager_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                emp["email"],
                hash_password(emp["password"]),
                emp["full_name"],
                emp["role"],
                emp["department"],
                emp["contract_type"],
                emp["hire_date"],
                emp["manager_name"]
            ))
            print(f"Compte créé : {emp['email']} ({emp['role']})")
        else:
            print(f"Compte existant : {emp['email']}")

    conn.commit()
    cur.close()
    conn.close()
    print("Seed terminé.")


if __name__ == "__main__":
    seed()