import os
import requests
from datetime import datetime, timezone, timedelta

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
REPO = os.environ['GITHUB_REPOSITORY']
WEBHOOK_URL = os.environ['GOOGLE_CHAT_WEBHOOK']

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Only get issues created in the last 10 minutes
since = datetime.now(timezone.utc) - timedelta(minutes=10)
since_str = since.strftime('%Y-%m-%dT%H:%M:%SZ')

url = f"https://api.github.com/repos/{REPO}/issues?state=open&sort=created&direction=asc&per_page=50&since={since_str}"
response = requests.get(url, headers=headers)
response.raise_for_status()
issues = response.json()

print(f"Found {len(issues)} issues since {since_str}")

for issue in issues:
    if 'pull_request' in issue:
        continue  # skip pull requests

    created_at = datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    
    if created_at < since:
        continue  # skip issues older than 10 minutes

    print(f"Sending notification for issue: {issue['title']}")

    message = {
        "cards": [{
            "header": {"title": "New GitHub Issue", "subtitle": REPO},
            "sections": [{
                "widgets": [
                    {"keyValue": {"topLabel": "Title", "content": issue['title']}},
                    {"keyValue": {"topLabel": "Opened by", "content": issue['user']['login']}},
                    {"keyValue": {"topLabel": "Created at", "content": issue['created_at']}},
                    {"buttons": [{"textButton": {"text": "View Issue", "onClick": {"openLink": {"url": issue['html_url']}}}}]}
                ]
            }]
        }]
    }

    resp = requests.post(WEBHOOK_URL, json=message)
    resp.raise_for_status()
    print(f"Notified: {issue['title']}")
