import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

PSX_URL = "https://dps.psx.com.pk/payouts"

# Pakistan timezone
pakistan_time = datetime.now(ZoneInfo("Asia/Karachi"))
today = pakistan_time.date()

print("PSX Dividend Alert Bot Started")
print("Pakistan Date:", today)

all_today_announcements = []

# PSX shows 25 records per page
count = 25
offset = 0

while True:

    print(f"Fetching records: offset={offset}")

    response = requests.post(
        PSX_URL,
        data={
            "symbol": "",
            "count": count,
            "offset": offset
        },
        timeout=30
    )

    print("PSX Response Status:", response.status_code)

    if response.status_code != 200:
        print("Failed to get PSX data")
        break

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", id="announcementsTable")

    if not table:
        print("Payout table not found")
        break

    tbody = table.find("tbody")

    if not tbody:
        print("Table body not found")
        break

    rows = tbody.find_all("tr")

    print(f"Records found on this page: {len(rows)}")

    # Stop if there are no more records
    if len(rows) == 0:
        break

    for row in rows:

        columns = row.find_all("td")

        if len(columns) >= 6:

            symbol = columns[0].get_text(strip=True)
            company = columns[1].get_text(strip=True)
            sector = columns[2].get_text(strip=True)
            dividend = columns[3].get_text(strip=True)
            announcement_date = columns[4].get_text(" ", strip=True)
            book_closure = columns[5].get_text(" ", strip=True)

            try:
                announcement_datetime = datetime.strptime(
                    announcement_date,
                    "%B %d, %Y %I:%M %p"
                )

                announcement_date_only = announcement_datetime.date()

            except ValueError:
                print("Could not parse date:", announcement_date)
                continue

            # Only today's announcements
            if announcement_date_only == today:

                announcement = {
                    "symbol": symbol,
                    "company": company,
                    "sector": sector,
                    "dividend": dividend,
                    "announcement_date": announcement_date,
                    "book_closure": book_closure
                }

                all_today_announcements.append(announcement)

    # Move to next page
    offset += count


print("--------------------------------")
print(
    f"Total announcements for {today}: "
    f"{len(all_today_announcements)}"
)

for announcement in all_today_announcements:

    print("--------------------------------")
    print("Symbol:", announcement["symbol"])
    print("Company:", announcement["company"])
    print("Sector:", announcement["sector"])
    print("Dividend:", announcement["dividend"])
    print("Announcement:", announcement["announcement_date"])
    print("Book Closure:", announcement["book_closure"])
