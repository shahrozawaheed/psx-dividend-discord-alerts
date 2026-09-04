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

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", id="announcementsTable")

    if table:

        rows = table.find("tbody").find_all("tr")

        print(f"Found {len(rows)} payout records")

        today_announcements = 0

        for row in rows:

            columns = row.find_all("td")

            if len(columns) >= 6:

                symbol = columns[0].get_text(strip=True)
                company = columns[1].get_text(strip=True)
                sector = columns[2].get_text(strip=True)
                dividend = columns[3].get_text(strip=True)
                announcement_date = columns[4].get_text(" ", strip=True)
                book_closure = columns[5].get_text(" ", strip=True)

                # Extract announcement date
                try:
                    announcement_datetime = datetime.strptime(
                        announcement_date,
                        "%B %d, %Y %I:%M %p"
                    )

                    announcement_date_only = announcement_datetime.date()

                except ValueError:
                    print("Could not parse date:", announcement_date)
                    continue

                # Match announcement date with today's Pakistan date
                if announcement_date_only == today:

                    today_announcements += 1

                    print("--------------------------------")
                    print("TODAY'S ANNOUNCEMENT")
                    print("Symbol:", symbol)
                    print("Company:", company)
                    print("Sector:", sector)
                    print("Dividend:", dividend)
                    print("Announcement:", announcement_date)
                    print("Book Closure:", book_closure)

        print("--------------------------------")
        print(
            f"Total announcements for {today}: "
            f"{today_announcements}"
        )

    else:
        print("Payout table not found")

else:
    print("Failed to get PSX data")
