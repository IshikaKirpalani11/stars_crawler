import os
import requests
import time

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

QUERY = """
query ($after: String) {
  search(query: "stars:>0", type: REPOSITORY, first: 100, after: $after) {
    pageInfo {
      endCursor
      hasNextPage
    }
    edges {
      node {
        ... on Repository {
          id
          name
          owner {
            login
          }
          stargazerCount
          url
        }
      }
    }
  }
}
"""

def fetch_repos(max_repos=100000, sleep_per_request=1):
    """
    Fetch up to max_repos repositories from GitHub with rate-limit handling.
    """
    url = "https://api.github.com/graphql"
    repos = []
    after = None

    while len(repos) < max_repos:
        variables = {"after": after}
        response = requests.post(url, json={"query": QUERY, "variables": variables}, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            search = data["data"]["search"]
            for edge in search["edges"]:
                node = edge["node"]
                repos.append(
                    (node["id"], node["name"], node["owner"]["login"], node["stargazerCount"], node["url"])
                )
            if not search["pageInfo"]["hasNextPage"]:
                break
            after = search["pageInfo"]["endCursor"]
        elif response.status_code == 403:
            # Rate limit reached, wait until reset
            reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
            sleep_seconds = reset_time - int(time.time())
            print(f"Rate limit reached. Sleeping for {sleep_seconds} seconds...")
            time.sleep(max(sleep_seconds, 1))
        else:
            print("Error:", response.status_code, response.text)
            time.sleep(10)

        print(f"Fetched {len(repos)} repositories so far...")
        time.sleep(sleep_per_request)  # small delay between requests

    return repos[:max_repos]
