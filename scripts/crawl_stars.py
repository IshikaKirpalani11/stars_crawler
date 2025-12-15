import os
import sys
from urllib.parse import urlparse

# Ensure repo root is on PYTHONPATH
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.infrastructure.github.crawler import fetch_repos
import psycopg2
from psycopg2.extras import execute_values


# -------------------------
# Configuration
# -------------------------
MAX_REPOS = int(os.getenv("MAX_REPOS", "100000"))
SLEEP_PER_REQUEST = float(os.getenv("SLEEP_PER_REQUEST", "1"))


def get_connection():
    """
    Supports DATABASE_URL (preferred) or individual env vars
    """
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return psycopg2.connect(database_url)

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "github"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", "postgres"),
        port=os.getenv("DB_PORT", 5432),
    )


def upsert_repos(repo_list):
    """
    repo_list = [
        (id, name, owner, stars, url)
    ]
    """
    if not repo_list:
        return

    conn = get_connection()
    cur = conn.cursor()

    query = """
    INSERT INTO github_repos (id, name, owner, stars, url, updated_at)
    VALUES %s
    ON CONFLICT (id)
    DO UPDATE SET
        stars = EXCLUDED.stars,
        updated_at = NOW()
    """

    execute_values(cur, query, repo_list)
    conn.commit()

    cur.close()
    conn.close()


def main():
    print(f"Starting GitHub repos fetch (max_repos={MAX_REPOS})")

    repos = fetch_repos(
        max_repos=MAX_REPOS,
        sleep_per_request=SLEEP_PER_REQUEST
    )

    print(f"Fetched {len(repos)} repos, saving to database...")
    upsert_repos(repos)

    print("Done!")


if __name__ == "__main__":
    main()
