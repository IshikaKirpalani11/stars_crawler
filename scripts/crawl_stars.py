import os
from app.infrastructure.github.crawler import fetch_repos
import psycopg2
from psycopg2.extras import execute_values

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "github")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_PORT = os.getenv("DB_PORT", 5432)

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

def upsert_repos(repo_list):
    """
    repo_list = [
        (id, name, owner, stars, url)
    ]
    """
    conn = get_connection()
    cur = conn.cursor()
    query = """
    INSERT INTO github_repos (id, name, owner, stars, url)
    VALUES %s
    ON CONFLICT (id)
    DO UPDATE SET stars = EXCLUDED.stars, updated_at = NOW()
    """
    execute_values(cur, query, repo_list)
    conn.commit()
    cur.close()
    conn.close()

def main():
    print("Starting GitHub repos fetch...")
    repos = fetch_repos(max_repos=100000, sleep_per_request=1)
    print(f"Fetched {len(repos)} repos, saving to database...")
    upsert_repos(repos)
    print("Done!")


if __name__ == "__main__":
    main()
