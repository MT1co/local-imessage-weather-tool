# iMessage Weather Tool

Sends a daily 3 day weather forecast to yourself via iMessage from a Mac running in the background. Useful for remote trips where you want to use Apple Satellite service to receive a weather briefing texted to your phone each morning. This saves you from having to use a Garmin or other satellite data service to receive the weather. 

**Example message:**
```
My Location weather: 15.3°C now, wind 8.5km/h.
Today: 12.9-22.9°C, 6% precip, sunrise 5:51am, sunset 9:45pm
Tomorrow: 13.5-18.9°C, 11% precip, sunrise 5:52am, sunset 9:45pm
Day 3: 9.9-25.3°C, 10% precip, sunrise 5:53am, sunset 9:44pm
```

Storm warnings appear automatically when precipitation probability ≥ 70% or wind gusts ≥ 50 km/h.

Weather data is sourced from [Open-Meteo](https://open-meteo.com/) (free, no API key required).

---

## Requirements

- macOS with Messages.app signed into your Apple ID
- Python 3
- `requests` library

---

## Setup

### 1. Place the script

Copy `weather_imessage.py` to a stable location on your Mac, e.g.:

```bash
mkdir -p ~/Scripts
cp weather_imessage.py ~/Scripts/
```

### 2. Edit the configuration

Open `weather_imessage.py` and set the variables at the top:

| Variable | Description |
|---|---|
| `LAT, LON` | Decimal coordinates of the location you want weather for |
| `PHONE` | Your iMessage-registered phone number, e.g. `+14165551234` |
| `TIMEZONE` | Your timezone string — see [tz database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) |
| `LOCATION_NAME` | Label used in the message, e.g. `"Algonquin"` |
| `STORM_PRECIP_THRESHOLD` | % precip probability that triggers a storm warning (default: 70) |
| `STORM_WIND_THRESHOLD` | Wind gust speed (km/h) that triggers a storm warning (default: 50) |

### 3. Install dependencies

```bash
pip3 install requests
```

> If you use pyenv, conda, or another Python manager, make sure you install into the same Python you'll use to run the script. Run `which python3` to confirm.

### 4. Test manually

```bash
python3 ~/Scripts/weather_imessage.py
```

Messages.app must be signed into your Apple ID and must have exchanged at least one message with your own number already, or the buddy lookup will fail.

### 5. Schedule with launchd (runs daily at 7am)

Edit `com.user.weathertext.plist` and replace `YOUR_USERNAME` with your macOS username (`whoami` in Terminal), and update the python3 path if needed (`which python3`).

Then load it:

```bash
cp com.user.weathertext.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.user.weathertext.plist
```

To change the time, edit the `Hour` and `Minute` values in the plist, then reload:

```bash
launchctl unload ~/Library/LaunchAgents/com.user.weathertext.plist
launchctl load ~/Library/LaunchAgents/com.user.weathertext.plist
```

Check logs at `/tmp/weathertext.out` and `/tmp/weathertext.err`.

### 6. Keep the Mac awake and reachable

The Mac needs to be on, awake, and connected to the internet at the scheduled time.

```bash
sudo pmset -a womp 1                                   # wake on network access
sudo pmset repeat wakeorpoweron MTWRFSU 06:55:00       # wake 5 min before the 7am run
```

---

## Apple Satellite

This requires the user to connect to Apple Satellite to receive the message. You can connect anytime and receive a backlog of messages. Ensure to test prior to any trips by activating airplane mode during the scheduled message time, then connecting to Apple Satellite service to ensure you can receive.
