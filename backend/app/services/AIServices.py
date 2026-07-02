import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize the async client (automatically picks up OPENAI_API_KEY from your .env file)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_tailored_cv(job_description: str, raw_title: str, raw_summary: str, raw_skills: str, raw_repositories: list) -> dict:
    """
    Evaluates all synced repositories against a job target, filters down to the 
    top 2 best fits, rewrites them using high-impact metrics, and returns the tailored CV.
    """
    
    system_prompt = (
        "You are an expert technical resume writer and career coach specializing in passing ATS filters.\n"
        "Your task is to take a user's current raw CV details and optimize them for a specific job target.\n"
        "Guidelines:\n"
        "- Do not lie or fabricate experience; instead, elevate the language, highlight relevant skills, and use strong action verbs.\n"
        "- The 'summary' should be a compelling paragraph (2-3 sentences).\n"
        "- The 'skills' should be a comma-separated list of the most relevant technical keywords.\n"
        "- CRITICAL MATCHMAKING RULE: Evaluate the provided list of repositories. Choose EXACTLY the top 2 repositories "
        "that have the absolute highest technical relevance to the target job description. Discard the rest.\n"
        "- For the chosen 2 repositories, optimize the 'role' to fit what the job description values, keep the exact same 'company' (repository name), "
        "and rewrite the 'desc' into punchy, metric-driven bullet points or lines using the STAR method.\n"
        "- You MUST respond ONLY with a raw JSON object matching the requested structure. Do not include markdown formatting like ```json ... ```."
    )
    
    user_content = f"""
    TARGET JOB REQUIREMENT/DESCRIPTION:
    {job_description}
    
    CURRENT RAW CV DETAILS:
    Title: {raw_title}
    Summary: {raw_summary}
    Skills: {raw_skills}
    Available Synced Repositories: {json.dumps(raw_repositories, indent=2)}
    
    Respond exactly in this JSON format:
    {{
        "title": "Optimized Job Title Match",
        "summary": "Optimized professional summary...",
        "skills": "Skill1, Skill2, Skill3...",
        "best_matched_repos": [
            {{
                "role": "Optimized Project Role Name",
                "company": "Repository Name 1",
                "desc": "Tailored project descriptions highlighting relevant stack elements..."
            }},
            {{
                "role": "Optimized Project Role Name",
                "company": "Repository Name 2",
                "desc": "Tailored project descriptions highlighting relevant stack elements..."
            }}
        ]
    }}
    """

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"}, 
            temperature=0.7
        )
        
        result_text = response.choices[0].message.content
        return json.loads(result_text)
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        raise e


async def analyze_github_with_ai(username: str, repos: list) -> dict:
    """
    Feeds a processed list of GitHub repositories to GPT-4o Mini 
    and returns parsed core skills and local/remote job matches.
    """
    
    system_prompt = (
        "You are an advanced technical talent analytics AI.\n"
        "Your job is to look at a tech student's public GitHub repository profile and compile an analytical summary.\n"
        "Instructions:\n"
        "- Identify their top 5 core technical skills or frameworks based on languages and project scopes.\n"
        "- Generate exactly 2 highly accurate, context-aware job matches based strictly on their implied skills profile.\n"
        "- Provide a specific match percentage (integer between 50 and 99).\n"
        "- Provide realistic local or remote companies and roles.\n"
        "- You MUST respond ONLY with a raw JSON object matching the requested structure without any markdown formatting wrappers."
    )
    
    user_content = f"""
    GITHUB USERNAME: {username}
    REPOSITORIES EVALUATION METRIC:
    {json.dumps(repos, indent=2)}
    
    Respond exactly in this JSON format:
    {{
        "core_skills": ["Skill1", "Skill2", "Skill3", "Skill4", "Skill5"],
        "job_matches": [
            {{
                "title": "Tech Student Role",
                "company": "Company Name",
                "location": "City or Remote",
                "match_percentage": 92
            }},
            {{
                "title": "Alternative Tech Role",
                "company": "Company Name",
                "location": "City or Remote",
                "match_percentage": 78
            }}
        ]
    }}
    """
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0.5
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"AI Analytics Error: {e}")
        raise e