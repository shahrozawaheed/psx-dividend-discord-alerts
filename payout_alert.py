```python
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
import time
import json
import hashlib

PSX_URL = "https://dps.psx.com.pk/payouts"
SENT_FILE = "sent_alerts.json"

# Discord webhook stored safely in GitHub Secrets
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Pakistan timezone
pakistan_time = datetime.now(ZoneInfo("Asia/Karachi"))
today = pakistan_time.date()

print("PSX Dividend Alert Bot Started")
print("Pakistan Date:", today)

# Check Discord webhook
if not DISCORD_WEBHOOK_URL:
    print("ERROR: DISCORD_WEBHOOK_URL secret is missing.")
    raise SystemExit(1)


# --------------------------------------------------
# Load previously sent announcements
# --------------------------------------------------

if os.path.exists(SENT_FILE):

    try:
        with open(SENT_FILE, "r", encoding="utf-8") as file:
            sent_alerts = set(json.load(file))

    except (json.JSONDecodeError, OSError):
        print("Could not read sent_alerts.json.")
        sent_alerts = set()

else:
    sent_alerts = set()

print("Previously sent alerts:", len(sent_alerts))


# --------------------------------------------------
# Get PSX data
# --------------------------------------------------

response = None

for attempt in range(1, 4):

    print(f"Request attempt: {attempt}")

    try:

        response = requests.post(
            PSX_URL,
            data={
                "symbol": "",
                "count": 25,
                "offset": 0
            },
            timeout=30
        )

        print("PSX Response Status:", response.status_code)

        if response.status_code == 200:
            break

        print("PSX request failed. Retrying...")

    except requests.RequestException as error:

        print("Request error:", error)

    time.sleep(5)


if response is None or response.status_code != 200:

    print("PSX data could not be retrieved.")
    raise SystemExit(1)


# --------------------------------------------------
# Parse PSX HTML
# --------------------------------------------------

soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table", id="announcementsTable")

if not table:

    print("Payout table not found.")
    raise SystemExit(1)


tbody = table.find("tbody")

if not tbody:

    print("Table body not found.")
    raise SystemExit(1)


rows = tbody.find_all("tr")

print(f"Found {len(rows)} payout records")


today_announcements = []


# --------------------------------------------------
# Read PSX records
# --------------------------------------------------

for row in rows:

    columns = row.find_all("td")

    if len(columns) < 6:
        continue

    symbol = columns[0].get_text(strip=True)
    company = columns[1].get_text(strip=True)
    sector = columns[2].get_text(strip=True)
    dividend = columns[3].get_text(strip=True)
    announcement_date = columns[4].get_text(" ", strip=True)
    book_closure = columns[5].get_text(" ", strip=True)

    # Parse announcement date
    try:

        announcement_datetime = datetime.strptime(
            announcement_date,
            "%B %d, %Y %I:%M %p"
        )

    except ValueError:

        print("Could not parse date:", announcement_date)
        continue

    announcement_date_only = announcement_datetime.date()

    # Only today's announcements
    if announcement_date_only == today:

        today_announcements.append({
            "symbol": symbol,
            "company": company,
            "sector": sector,
            "dividend": dividend,
            "announcement_date": announcement_date,
            "book_closure": book_closure
        })


print("--------------------------------")
print(
    f"Total announcements for {today}: "
    f"{len(today_announcements)}"
)
print("--------------------------------")


# --------------------------------------------------
# Send announcements to Discord
# --------------------------------------------------

new_alerts_sent = False

for announcement in today_announcements:

    # Create a unique ID for this announcement
    unique_string = (
        announcement["symbol"]
        + "|"
        + announcement["company"]
        + "|"
        + announcement["sector"]
        + "|"
        + announcement["dividend"]
        + "|"
        + announcement["announcement_date"]
        + "|"
        + announcement["book_closure"]
    )

    alert_id = hashlib.sha256(
        unique_string.encode("utf-8")
    ).hexdigest()

    # Check if already sent
    if alert_id in sent_alerts:

        print(
            f"SKIPPED duplicate: "
            f"{announcement['symbol']} "
            f"{announcement['announcement_date']}"
        )

        continue


    # Keep PSX values exactly as provided
    message = (
        f"Symbol: {announcement['symbol']}\n"
        f"Company: {announcement['company']}\n"
        f"Sector: {announcement['sector']}\n"
        f"Dividend: {announcement['dividend']}\n"
        f"Date / Time of Announcement: "
        f"{announcement['announcement_date']}\n"
        f"Book Closure Date: {announcement['book_closure']}"
    )


    discord_response = requests.post(
        DISCORD_WEBHOOK_URL,
        json={
            "content": message
        },
        timeout=30
    )


    print(
        f"Discord response for "
        f"{announcement['symbol']}: "
        f"{discord_response.status_code}"
    )


    if discord_response.status_code in (200, 204):

        print(
            f"Successfully sent "
            f"{announcement['symbol']} "
            "to Discord."
        )

        # Mark as sent ONLY after successful Discord delivery
        sent_alerts.add(alert_id)
        new_alerts_sent = True

    else:

        print(
            f"Failed to send "
            f"{announcement['symbol']} "
            "to Discord."
        )

        print(discord_response.text)


    # Small delay between Discord messages
    time.sleep(1)


# --------------------------------------------------
# Save sent announcements
# --------------------------------------------------

if new_alerts_sent:

    with open(SENT_FILE, "w", encoding="utf-8") as file:

        json.dump(
            sorted(sent_alerts),
            file,
            indent=2
        )

    print(
        f"Saved {len(sent_alerts)} sent alerts "
        "to sent_alerts.json"
    )

else:

    print("No new alerts were sent.")


print("--------------------------------")
print("PSX Dividend Alert Bot Finished")
```
