import os
import requests
from datetime import datetime, timezone, timedelta

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
REPO = "Expensify/App"
WEBHOOK_URL = os.environ['GOOGLE_CHAT_WEBHOOK']
LAST_RUN_FILE = "last_run.txt"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# Read last run time, default to 60 mins ago if first run
if os.path.exists(LAST_RUN_FILE):
    with open(LAST_RUN_FILE) as f:
        since_str = f.read().strip()
    since = datetime.strptime(since_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
else:
    since = datetime.now(timezone.utc) - timedelta(minutes=15)
    since_str = since.strftime('%Y-%m-%dT%H:%M:%SZ')

# Save current time as next run's "since"
now_str = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
with open(LAST_RUN_FILE, "w") as f:
    f.write(now_str)

print(f"Monitoring repo: {REPO}")
print(f"Looking for issues created after: {since_str}")

url = f"https://api.github.com/repos/{REPO}/issues?state=open&sort=created&direction=desc&per_page=50"
response = requests.get(url, headers=headers)
response.raise_for_status()
issues = response.json()

print(f"Total issues fetched: {len(issues)}")

notified = 0
for issue in issues:
    if 'pull_request' in issue:
        continue

    created_at = datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)

    if created_at <= since:
        print(f"-> Too old, stopping.")
        break

    print(f"Notifying: #{issue['number']} - {issue['title'][:60]}")

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
