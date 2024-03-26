import base64
import requests

def fetch_and_parse_codeowners_multiple_repos(repo_list, github_token):
    """
    Fetch and parse CODEOWNERS files from multiple repositories.
    
    :param repo_list: List of tuples containing the repo_owner and repo_name.
    :param github_token: GitHub Access Token for API authentication.
    :return: A set of unique code owners across all provided repositories.
    """
    all_code_owners = set()
    for repo_owner, repo_name in repo_list:
        code_owners = fetch_and_parse_codeowners(repo_owner, repo_name, github_token)
        all_code_owners.update(code_owners)
    return all_code_owners

def fetch_and_parse_codeowners(repo_owner, repo_name, github_token):
    """
    Fetch and parse the CODEOWNERS file from a GitHub repository.
    """
    codeowners_paths = [".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS"]
    headers = {'Authorization': f'token {github_token}'}
    base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/"

    for path in codeowners_paths:
        response = requests.get(base_url + path, headers=headers)
        if response.status_code == 200:
            content = base64.b64decode(response.json()['content']).decode('utf-8')
            return parse_codeowners_content(content)

    return set()  # Return an empty set if the CODEOWNERS file is not found

def parse_codeowners_content(content):
    """
    Parse the content of a CODEOWNERS file to extract GitHub usernames and teams.
    """
    code_owners = set()
    for line in content.split('\n'):
        if line.strip() and not line.startswith('#'):
            parts = line.split()
            for part in parts[1:]:  # Skip the pattern part
                if part.startswith('@'):
                    username_or_team = part[1:].split('#')[0].strip()
                    code_owners.add(username_or_team)
    return code_owners

# Define the repositories from which to fetch CODEOWNERS files
repo_list = [
    ('department-of-veterans-affairs', 'vets-api'),
    ('department-of-veterans-affairs', 'vets-website'),
    ('department-of-veterans-affairs', 'devops'),
]

# Use your GitHub token here
GITHUB_TOKEN = 'your_github_token_here'

# Fetch and parse CODEOWNERS
all_code_owners = fetch_and_parse_codeowners_multiple_repos(repo_list, GITHUB_TOKEN)
print(all_code_owners)
