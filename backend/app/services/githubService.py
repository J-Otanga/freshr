# services/github_service.py
import httpx
import re
from fastapi import HTTPException

async def fetch_github_repositories(github_url: str) -> list:
    """
    Parses the username from a GitHub URL and fetches all public repository data.
    """
    # 1. Clean and extract username
    match = re.search(r"github\.com/([^/]+)", github_url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL format.")
    
    username = match.group(1).strip()
    
    # 2. Query GitHub API asynchronously
    url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Freshr-App-Backend" # GitHub requires a User-Agent header
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"GitHub user '{username}' not found.")
            elif response.status_code == 403:
                raise HTTPException(status_code=403, detail="GitHub API rate limit exceeded. Please try again later.")
            elif response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch data from GitHub.")
                
            repos_data = response.json()
            
            # 3. Clean up the payload to only keep what the AI needs
            processed_repos = []
            for repo in repos_data:
                # Skip forks to focus on the user's original work
                if repo.get("fork"):
                    continue
                    
                processed_repos.append({
                    "name": repo.get("name"),
                    "description": repo.get("description") or "No description provided.",
                    "language": repo.get("language"),
                    "stars": repo.get("stargazers_count", 0)
                })
                
            return processed_repos

        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"GitHub service unavailable: {str(e)}")