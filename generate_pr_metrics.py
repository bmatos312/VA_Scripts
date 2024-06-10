import json
import sys
from datetime import datetime

def calculate_time_open(created_at, closed_at):
    created_date = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
    closed_date = datetime.strptime(closed_at, '%Y-%m-%dT%H:%M:%SZ') if closed_at else datetime.utcnow()
    return (closed_date - created_date).days

def is_check_passing(checks):
    for check in checks:
        status = check['commit'].get('status')
        if status is None:
            continue  # If status is None, skip this check
        contexts = status['contexts']
        for context in contexts:
            if context['context'] != "codeclimate":
                if context['state'] != "SUCCESS":
                    return False
    return True

def generate_markdown(pr_data):
    report_lines = [
        "# Weekly Pull Request Metrics Report\n",
        "| PR Number | Title | Time Open (days) | Checks Passing | Codeowner Reviews |\n",
        "|-----------|-------|------------------|----------------|-------------------|\n",
    ]
    
    for pr in pr_data:
        pr_number = pr['number']
        title = pr['title']
        time_open = calculate_time_open(pr['createdAt'], pr['closedAt'])
        checks_passing = "Passing" if is_check_passing(pr['commits']['nodes']) else "Failing"
        codeowner_reviews = ", ".join(
            [review['author']['login'] for review in pr['reviews']['nodes'] if review['author']['login']]
        )
        report_lines.append(f"| {pr_number} | {title} | {time_open} | {checks_passing} | {codeowner_reviews} |\n")
    
    with open('pull_request_metrics.md', 'w') as file:
        file.writelines(report_lines)

def main():
    with open('prs.json', 'r') as file:
        pr_data = json.load(file)
    
    print("PR Data Loaded:", json.dumps(pr_data, indent=2))
    
    generate_markdown(pr_data)

if __name__ == "__main__":
    main()
