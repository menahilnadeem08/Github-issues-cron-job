import os
import requests

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
REPO = os.environ['GITHUB_REPOSITORY']
WEBHOOK_URL = os.environ['GOOGLE_CHAT_WEBHOOK']
# Passed in from the workflow as an env var (stored as a secret or cache artifact)
LAST_ISSUE_ID = int(os.environ.get('LAST_ISSUE_ID', '0'))

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

url = f"https://api.github.com/repos/{REPO}/issues?state=open&sort=created&direction=asc&per_page=50"
response = requests.get(url, headers=headers)
response.raise_for_status()
issues = response.json()

new_last_id = LAST_ISSUE_ID

for issue in issues:
    if issue['id'] > LAST_ISSUE_ID and 'pull_request' not in issue:
        message = {
            "cards": [{
                "header": {"title": "New GitHub Issue", "subtitle": REPO},
                "sections": [{
                    "widgets": [
                        {"keyValue": {"topLabel": "Title", "content": issue['title']}},
                        {"keyValue": {"topLabel": "Opened by", "content": issue['user']['login']}},
                        {"buttons": [{"textButton": {"text": "View Issue", "onClick": {"openLink": {"url": issue['html_url']}}}}]}
                    ]
                }]
            }]
        }
        resp = requests.post(WEBHOOK_URL, json=message)
        resp.raise_for_status()
        new_last_id = max(new_last_id, issue['id'])

# Write new ID to file so the workflow can cache it
with open("last_issue_id.txt", "w") as f:
    f.write(str(new_last_id))
