import os
import requests


GITHUB_API = "https://api.github.com"


def _headers() -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _parse_owner_repo(url: str) -> tuple[str, str]:
    """Extract owner and repo name from a GitHub URL."""
    url = url.rstrip("/").removesuffix(".git")
    parts = url.split("/")
    # handle https://github.com/owner/repo or owner/repo
    owner = None
    repo = None
    if "github.com" in url:
        owner = parts[-2]
        repo = parts[-1]
    elif len(parts) == 2:
        owner, repo = parts
    else:
        raise ValueError(f"Cannot parse GitHub URL: {url}")
    return owner, repo


def get_repo_info(url: str) -> dict:
    """Fetch repository metadata from GitHub API."""
    owner, repo = _parse_owner_repo(url)
    resp = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}",
        headers=_headers(),
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    return {
        "name": data.get("full_name", ""),
        "description": data.get("description") or "",
        "stars": data.get("stargazers_count", 0),
        "language": data.get("language") or "Unknown",
        "topics": data.get("topics", []),
        "default_branch": data.get("default_branch", "main"),
        "url": data.get("html_url", url),
    }


def get_dependencies(url: str) -> list[str]:
    """Read requirements.txt or package.json from the repo root."""
    owner, repo = _parse_owner_repo(url)
    deps: list[str] = []

    for filename in ("requirements.txt", "pyproject.toml", "package.json"):
        resp = requests.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/contents/{filename}",
            headers=_headers(),
            timeout=15,
        )
        if resp.status_code != 200:
            continue
        import base64
        import json

        content = base64.b64decode(resp.json()["content"]).decode("utf-8", errors="replace")

        if filename == "requirements.txt":
            deps = [
                line.strip().split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0]
                for line in content.splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
            break

        if filename == "package.json":
            pkg = json.loads(content)
            deps = list(pkg.get("dependencies", {}).keys())
            break

        if filename == "pyproject.toml":
            in_deps = False
            for line in content.splitlines():
                if "[project.dependencies]" in line or "dependencies = [" in line:
                    in_deps = True
                    continue
                if in_deps:
                    if line.strip().startswith("]"):
                        break
                    dep = line.strip().strip('"').strip("'").split(">=")[0].split("<=")[0].split("~=")[0].split("==")[0]
                    if dep:
                        deps.append(dep)
            break

    return deps


def search_repos(query: str, limit: int = 5) -> list[dict]:
    """Search GitHub repositories matching a query."""
    resp = requests.get(
        f"{GITHUB_API}/search/repositories",
        params={"q": query, "sort": "stars", "order": "desc", "per_page": limit},
        headers=_headers(),
        timeout=15,
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])
    results = []
    for item in items:
        repo_url = item.get("html_url", "")
        deps = []
        try:
            deps = get_dependencies(repo_url)
        except Exception:
            pass
        results.append({
            "name": item.get("full_name", ""),
            "description": item.get("description") or "",
            "stars": item.get("stargazers_count", 0),
            "language": item.get("language") or "Unknown",
            "topics": item.get("topics", []),
            "dependencies": deps,
            "url": repo_url,
        })
    return results
