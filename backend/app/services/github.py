import httpx
from fastapi import HTTPException

async def get_student_languages(github_url: str):
    """
    Takes a GitHub URL or username, asks GitHub for their repositories,
    and calculates their top programming languages.
    """
    # Clean up the input in case they entered a full link like "https://github.com/user"
    username = github_url.split("/")[-1].strip()
    
    # GitHub's public API endpoint for a user's repositories
    url = f"https://api.github.com/users/{username}/repos"
    
    # We must provide a User-Agent header, otherwise GitHub blocks the request
    headers = {"User-Agent": "Freshr-Backend-App"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            
            # If the username doesn't exist on GitHub, return an error safely
            if response.status_code == 404:
                raise HTTPException(status_code=400, detail="GitHub username not found")
                
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to fetch data from GitHub")
                
            repositories = response.json()
            
            # Count the programming languages across all their repositories
            language_counts = {}
            for repo in repositories:
                lang = repo.get("language")
                if lang:  # If the repository actually has a primary language specified
                    language_counts[lang] = language_counts.get(lang, 0) + 1
            
            # Sort them so the most used language is at the top
            sorted_languages = sorted(language_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Return a clean dictionary of languages, e.g., {"Python": 5, "JavaScript": 2}
            return dict(sorted_languages)

        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="GitHub API is temporarily unavailable")