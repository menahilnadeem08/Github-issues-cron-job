import os
import requests
from datetime import datetime, timezone, timedelta

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
REPO = "Expensify/App"
WEBHOOK_URL = os.environ['GOOGLE_CHAT_WEBHOOK']

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

since = datetime.now(timezone.utc) - timedelta(minutes=60)
since_str = since.strftime('%Y-%m-%dT%H:%M:%SZ')

# Remove &since= from URL, sort by created desc to get newest first
url = f"https://api.github.com/repos/{REPO}/issues?state=open&sort=created&direction=desc&per_page=50"
response = requests.get(url, headers=headers)
response.raise_for_status()
issues = response.json()

print(f"Monitoring repo: {REPO}")
print(f"Looking for issues created after: {since_str}")
print(f"Total issues fetched: {len(issues)}")

notified = 0
for issue in issues:
    if 'pull_request' in issue:
        continue

    created_at = datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)

    print(f"Issue #{issue['number']} created at {issue['created_at']} - {issue['title'][:50]}")

    if created_at < since:
        print(f"  -> Too old, stopping.")
        break  # since sorted desc, all remaining are older

    print(f"  -> Sending notification...")
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
    notified += 1
    print(f"  -> Notified!")

print(f"Done. Notified {notified} issues.")
