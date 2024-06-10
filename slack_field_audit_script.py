import requests
import pandas as pd
import time

SLACK_TOKEN = 'SLACK_TOKEN'  # Replace with your actual token
USERS_URL = 'https://slack.com/api/users.list'
HEADERS = {'Authorization': f'Bearer {SLACK_TOKEN}'}


def fetch_users():
    response = requests.get(USERS_URL, headers=HEADERS)
    if response.status_code == 200 and response.json().get('ok'):
        return response.json().get('members', [])
    elif response.status_code == 429:  # Rate limit hit
        retry_after = int(response.headers.get('Retry-After', 60))  # Use default of 60 seconds if header is missing
        print(f"Rate limited. Retrying in {retry_after} seconds.")
        time.sleep(retry_after)
        return fetch_users()  # Recursively retry
    else:
        print("Failed to fetch users:", response.text)
        return []

def compile_user_data(users):
    user_data = []
    for user in users:
        if not user.get('is_bot'):  # Skipping bots
            profile = user.get('profile', {})
            print(f"Debug Profile for {user.get('real_name')}: {profile}")  # Debug print

            email = profile.get('email')
            print(f"Debug Email for {user.get('real_name')}: {email}")  # Debug print

            # Assuming you have the correct field ID for roles and organization
            #roles_field_id = 'XfYOUR_CUSTOM_FIELD_ID_FOR_ROLES'  # Replace with the actual ID
            organization_field_id = 'organization_field_id'  # You confirmed this ID
            
            roles = profile.get('fields', {}).get(roles_field_id, {}).get('value', '') if profile.get('fields') else ''
            organization = profile.get('fields', {}).get(organization_field_id, {}).get('value', '') if profile.get('fields') else ''

            user_data.append({
                'Name': user.get('real_name'),
                'Email': email,
                #'Roles': roles,
                'Organization': organization,
            })
    return user_data

    return user_data


def export_to_excel(user_data):
    df = pd.DataFrame(user_data)
    df.to_excel('slack_users.xlsx', index=False)
    print("User data exported to slack_users.xlsx")

if __name__ == "__main__":
    users = fetch_users()
    user_data = compile_user_data(users)
    export_to_excel(user_data)
