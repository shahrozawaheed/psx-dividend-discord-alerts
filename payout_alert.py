import requests
from bs4 import BeautifulSoup
from datetime import datetime

PSX_URL = "https://dps.psx.com.pk/payouts"

print("PSX Dividend Alert Bot Started")

today = datetime.now().strftime("%Y-%m-%d")
print("Today's date:", today)

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
    print("PSX data received successfully")
else:
    print("Failed to get PSX data")
