import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db_config = {
    'dbname' : os.getenv('DB_NAME'),
    'user' : os.getenv('DB_USER'),
    'password' : os.getenv('DB_PASSWORD'),
    'host' : os.getenv('DB_HOST', 'localhost'),
    'port' : os.getenv('DB_PORT', '5432')
}

def setup_database():
    conn = None

    try:
        if not db_config['password']:
            raise ValueError("A senha do banco não foi encontrada no .env")
        
        print(f"Conectando em {db_config['host']}...")

        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        print("Conectado ao PostgreSQL via Docker.")

        with open('queries.sql', 'r', encoding='utf-8') as f:
            ddl_script = f.read()

        print("Criando tabelas...")
        cur.execute(ddl_script)

        conn.commit()
        print("Tabelas criadas com sucesso!")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    setup_database()