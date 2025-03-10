import requests
import json
from datetime import datetime
import pytz

# CTFtime API URL (Fetch next 10 upcoming CTFs)
CTFTIME_API_URL = "https://ctftime.org/api/v1/events/?limit=10"

# Headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Microsoft Teams Webhook Bot URL (Replace with your actual webhook URL)
TEAMS_WEBHOOK_URL = <Put your URL in string format at here>

def convert_to_myt(utc_time):
    """Convert UTC time to Malaysia Time (MYT)."""
    try:
        utc_datetime = datetime.strptime(utc_time, "%Y-%m-%dT%H:%M:%S%z")
        myt = pytz.timezone("Asia/Kuala_Lumpur")
        myt_datetime = utc_datetime.astimezone(myt)
        return myt_datetime
    except Exception as e:
        return None  # Return None if conversion fails

def get_time_left(start_time_myt):
    """Calculate time left until the CTF starts."""
    now_myt = datetime.now(pytz.timezone("Asia/Kuala_Lumpur"))
    time_diff = start_time_myt - now_myt

    if time_diff.total_seconds() > 0:
        days = time_diff.days
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"⏳ **Time Left:** {days}d {hours}h {minutes}m"
    else:
        return "✅ **Already Started!**"

def get_upcoming_ctfs():
    """Fetch upcoming CTF competitions from CTFtime API."""
    response = requests.get(CTFTIME_API_URL, headers=headers)

    if response.status_code == 200:
        events = response.json()
        if not events:
            return "❌ No upcoming CTF competitions found."

        # Format the CTF data into a Teams-friendly message
        message = "**🎯 Upcoming CTF Competitions 🎯**\n\n"
        for event in events:
            start_time_myt = convert_to_myt(event['start'])
            end_time_myt = convert_to_myt(event['finish'])

            if start_time_myt and end_time_myt:
                start_str = start_time_myt.strftime("%Y-%m-%d %H:%M:%S %Z")
                end_str = end_time_myt.strftime("%Y-%m-%d %H:%M:%S %Z")
                time_left_msg = get_time_left(start_time_myt)

                message += f"📌 **{event['title']}**\n"
                message += f"📅 **Start:** {start_str}\n"
                message += f"🕒 **End:** {end_str}\n"
                message += f"{time_left_msg}\n"
                message += f"🔗 [More Info]({event['url']})\n\n"
            else:
                message += f"⚠️ **Error processing time for {event['title']}**\n\n"

        return message
    else:
        return "⚠️ Failed to fetch CTF events from CTFtime."

def send_to_teams():
    """Send the CTF event data to Microsoft Teams Webhook."""
    ctf_message = get_upcoming_ctfs()

    payload = {"text": ctf_message}  # Teams webhook expects JSON payload
    headers = {"Content-Type": "application/json"}

    response = requests.post(TEAMS_WEBHOOK_URL, data=json.dumps(payload), headers=headers)

    if response.status_code in [200, 204]:
        print("✅ CTF updates sent successfully to Microsoft Teams!")
    else:
        print(f"❌ Failed to send message. HTTP Error: {response.status_code}")

# Run the function to send CTF updates
send_to_teams()
