#!/usr/bin/env python3
"""
Fetches weather for a fixed location and texts it to yourself via iMessage.
Run manually to test, then schedule via launchd (see com.user.weathertext.plist).
"""
import requests
import subprocess
import sys

# --- Configuration (edit these) ---
LAT, LON = 0.00, 0.00           # your target coordinates (decimal degrees)
PHONE = "+1XXXXXXXXXX"          # your iMessage-registered phone number
TIMEZONE = "America/Toronto"    # your timezone — see https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
LOCATION_NAME = "My Location"   # label used in the message

STORM_PRECIP_THRESHOLD = 70     # % precipitation probability to trigger storm warning
STORM_WIND_THRESHOLD = 50       # km/h wind gusts to trigger storm warning


def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "current": "temperature_2m,wind_speed_10m,precipitation",
        "daily": (
            "temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max,wind_gusts_10m_max,sunrise,sunset"
        ),
        "temperature_unit": "celsius",
        "timezone": TIMEZONE,
        "forecast_days": 3,
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def fmt_time(iso):
    from datetime import datetime
    return datetime.strptime(iso, "%Y-%m-%dT%H:%M").strftime("%-I:%M%p").lower()


def format_message(data):
    cur = data["current"]
    daily = data["daily"]

    warnings = []
    for i, label in enumerate(["today", "tomorrow", "day 3"]):
        precip = daily["precipitation_probability_max"][i]
        gusts = daily["wind_gusts_10m_max"][i]
        if precip >= STORM_PRECIP_THRESHOLD or gusts >= STORM_WIND_THRESHOLD:
            warnings.append(
                f"⚠️ Storm warning {label}: {precip}% precip, gusts {gusts}km/h"
            )

    days = []
    labels = ["Today", "Tomorrow", "Day 3"]
    for i, label in enumerate(labels):
        rise = fmt_time(daily["sunrise"][i])
        sset = fmt_time(daily["sunset"][i])
        days.append(
            f"{label}: {daily['temperature_2m_min'][i]}-{daily['temperature_2m_max'][i]}°C, "
            f"{daily['precipitation_probability_max'][i]}% precip, "
            f"sunrise {rise}, sunset {sset}"
        )

    parts = [f"{LOCATION_NAME} weather: {cur['temperature_2m']}°C now, wind {cur['wind_speed_10m']}km/h."]
    if warnings:
        parts.extend(warnings)
    parts.extend(days)
    return "\n".join(parts)


def send_imessage(text, phone):
    script = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "{phone}" of targetService
        send "{text}" to targetBuddy
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)


def main():
    try:
        data = get_weather()
        msg = format_message(data)
        send_imessage(msg, PHONE)
        print(f"Sent: {msg}")
    except Exception as e:
        print(f"Failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
