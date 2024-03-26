from flask import Flask, request, jsonify
import os
import re
import requests
from datetime import datetime, timezone, timedelta
from slack_sdk import WebClient
import logging

app = Flask(__name__)

# Placeholder for tokens and IDs
GITHUB_TOKEN = 'GITHUB_TOKEN'
SLACK_BOT_TOKEN = 'SLACK_BOT_TOKEN'
SLACK_CHANNEL = 'CBU0KDSB1'  # Ensure this is correct

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

bot_user_id = client.auth_test().get('user_id')

latest_ts = "0"

def fetch_and_parse_codeowners(repo_owner, repo_name):
    # Fetch the CODEOWNERS file content from the GitHub repository
    # Parse the file to determine code owners
    # Return a list or set of code owner GitHub usernames
    return {"codeowner1", "codeowner2"}

@app.route('/slack/events', methods=['POST'])
def slack_events():
    global latest_ts
    data = request.json
    logger.debug(f"Received data: {data}")  # Log incoming data

    event_type = data.get('type')

    if event_type == 'url_verification':
        return jsonify({'challenge': data.get('challenge')})
    
    event_data = data.get('event', {})
    if event_data.get('type') == 'message' and 'subtype' not in event_data:
        message_ts = event_data.get('ts', '0')
        if event_data.get('user') == bot_user_id or message_ts <= latest_ts:
            return jsonify({'status': 'ignored'}), 200
        latest_ts = message_ts

        channel_id = event_data['channel']
        thread_ts = event_data.get('thread_ts', event_data['ts'])
        message_text = event_data.get('text', '')

        match = re.search(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", message_text)
        if match:
            repo_owner, repo_name, pr_number = match.groups()
            pr_details_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
            pr_details_response = requests.get(pr_details_url, headers={'Authorization': f'token {GITHUB_TOKEN}'})
            if pr_details_response.status_code == 200:
                pr_data = pr_details_response.json()
                head_sha = pr_data['head']['sha']
                checks_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits/{head_sha}/check-runs"
                checks_response = requests.get(checks_url, headers={'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'})

                # Time difference calculation
                review_requested_at = pr_data.get('created_at')
                review_requested_at_datetime = datetime.strptime(review_requested_at, '%Y-%m-%dT%H:%M:%SZ')
                review_requested_at_datetime = review_requested_at_datetime.replace(tzinfo=timezone.utc)
                now_datetime = datetime.now(timezone.utc)
                time_diff = now_datetime - review_requested_at_datetime
                over_24_hours = time_diff > timedelta(hours=24)
                time_status = "and has been over 24 hours" if over_24_hours else "and has not been over 24 hours"
                time_status += " since the PR was requested for review."

            if checks_response.status_code == 200:
                checks_data = checks_response.json()
                failed_checks = [check['name'] for check in checks_data['check_runs'] if check['conclusion'] != 'success']

                if failed_checks:
                    checks_message = f":x: Required checks failed for PR #{pr_number}: " + ", ".join(failed_checks)
                else:
                    checks_message = f":white_check_mark: All required checks passed for PR #{pr_number}"

                # Concatenate checks_message with time_status
                message = f"{checks_message} {time_status}"
            else:
                message = "Failed to retrieve PR checks from GitHub."
        else:
            message = "Failed to retrieve PR details from GitHub."
        
        repo_owner, repo_name = pr_data['base']['repo']['owner']['login'], pr_data['base']['repo']['name']
        code_owners = fetch_and_parse_codeowners(repo_owner, repo_name)
        
        # Fetch the list of requested reviewers
        review_requests_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/requested_reviewers"
        review_requests_response = requests.get(review_requests_url, headers={'Authorization': f'token {GITHUB_TOKEN}'})
        review_requests_data = review_requests_response.json() if review_requests_response.status_code == 200 else {}

        requested_reviewers = {reviewer['login'] for reviewer in review_requests_data.get('users', [])}
        is_code_owner_review_requested = bool(requested_reviewers & code_owners)
        
        # Fetch the list of PR reviews to check if a non-code owner has reviewed it
        reviews_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews"
        reviews_response = requests.get(reviews_url, headers={'Authorization': f'token {GITHUB_TOKEN}'})
        reviews_data = reviews_response.json() if reviews_response.status_code == 200 else []

        non_code_owner_reviews = [review['user']['login'] for review in reviews_data if review['user']['login'] not in code_owners and review['state'].lower() == 'approved']

        review_status_message = ""
        if is_code_owner_review_requested:
            review_status_message += "Code Owner Review Requested. "
        if non_code_owner_reviews:
            review_status_message += f"Approved by non-code owners: {', '.join(non_code_owner_reviews)}."
        else:
            review_status_message += "No non-code owner reviews yet."

        # Use `review_status_message` in your message to Slack
        message = f"{review_status_message} {message}"

        response = client.chat_postMessage(channel=channel_id, text=message, thread_ts=thread_ts)
        if response.status_code == 200:
            logger.debug("Message posted to Slack")
        else:
            logger.debug("Failed to post message to Slack")
        return jsonify({'status': 'ok'}), 200

    return jsonify({'status': 'ignored'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
