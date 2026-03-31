import os
import requests

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
REPO = os.environ['GITHUB_REPOSITORY']
WEBHOOK_URL = os.environ['GOOGLE_CHAT_WEBHOOK']
LAST_ISSUE_FILE = "last_issue_id.txt"

headers = {"Authorization": f"token {GITHUB_TOKEN}"}

# Load last processed issue ID
if os.path.exists(LAST_ISSUE_FILE):
    with open(LAST_ISSUE_FILE, "r") as f:
        last_issue_id = int(f.read().strip())
else:
    last_issue_id = 0

# Fetch issues
url = f"https://api.github.com/repos/{REPO}/issues?state=open&sort=created&direction=asc"
response = requests.get(url, headers=headers)
issues = response.json()

new_last_id = last_issue_id

for issue in issues:
    if issue['id'] > last_issue_id and 'pull_request' not in issue:
        # Send to Google Chat
        data = {
            "text": f"**New GitHub Issue**\nTitle: {issue['title']}\nURL: {issue['html_url']}\nCreated by: {issue['user']['login']}"
        }
        requests.post(WEBHOOK_URL, json=data)
        new_last_id = max(new_last_id, issue['id'])

# Update last processed ID
with open(LAST_ISSUE_FILE, "w") as f:
    f.write(str(new_last_id))
