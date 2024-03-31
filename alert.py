import math
import time
from opensky_api import OpenSkyApi

MY_LATITUDE = 41.4995
MY_LONGITUDE = -81.69541
ALERT_DISTANCE = 3
RANGE = 1
OPENSKY_USERNAME = ''
OPENSKY_PASSWORD = ''
CHILL = 3600
DEFAULT_API_CALL_INTERVAL = 10
ALERT_API_CALL_INTERVAL = 5
API_CALL_INTERVAL = DEFAULT_API_CALL_INTERVAL

def get_aircraft_data():
    bbox_range = RANGE
    min_latitude = MY_LATITUDE - bbox_range
    max_latitude = MY_LATITUDE + bbox_range
    min_longitude = MY_LONGITUDE - bbox_range
    max_longitude = MY_LONGITUDE + bbox_range

    bbox = (min_latitude, max_latitude, min_longitude, max_longitude)
    api = OpenSkyApi(OPENSKY_USERNAME, OPENSKY_PASSWORD)
    try:
        states = api.get_states(bbox=bbox)
        #print(f"API Response: {states}")
        if states and states.states:
            #print(f"Retrieved {len(states.states)} aircraft states within major RANGE")
            return states.states
        else:
            print("No aircraft data available in the specified area.")
            print(time.strftime('%Y-%m-%d %H:%M:%S'))
            return []
    except Exception as e:
        if '429' in str(e):
            print("Rate limit exceeded. Waiting before next request.")
            print(time.strftime('%Y-%m-%d %H:%M:%S'))
            print()
            time.sleep(CHILL)
            print(time.strftime('%Y-%m-%d %H:%M:%S'))
            print()
        else:
            print(f"Error: {e}")
            print(time.strftime('%Y-%m-%d %H:%M:%S'))
            print()
        return []

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def check_aircraft_proximity(aircraft_data):
    alert_triggered = False
    for state_vector in aircraft_data:
        aircraft_lat, aircraft_lon = state_vector.latitude, state_vector.longitude
        if aircraft_lat and aircraft_lon:
            distance = calculate_distance(MY_LATITUDE, MY_LONGITUDE, aircraft_lat, aircraft_lon)
            if distance < ALERT_DISTANCE:
                trigger_alert(state_vector)
                alert_triggered = True
    return alert_triggered

def trigger_alert(state_vector):
    heading = state_vector.heading if hasattr(state_vector, 'heading') else 'Unknown'

    alert_message = (
        f"Alert: Aircraft {state_vector.callsign} is within proximity. "
        f"Origin Country: {state_vector.origin_country}, "
        f"Altitude: {state_vector.baro_altitude} meters, "
        f"Velocity: {state_vector.velocity} m/s, "
        f"Heading: {heading} degrees, "  # Including heading in the alert
        f"On Ground: {'Yes' if state_vector.on_ground else 'No'}, "
        f"Last Contact: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(state_vector.last_contact))} UTC"
    )
    print(alert_message)
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
    print()

def main():
    global API_CALL_INTERVAL
    while True:
        aircraft_data = get_aircraft_data()
        alert_triggered = check_aircraft_proximity(aircraft_data)
        if alert_triggered:
            API_CALL_INTERVAL = ALERT_API_CALL_INTERVAL  # use shortened interval
        else:
            API_CALL_INTERVAL = DEFAULT_API_CALL_INTERVAL  # reset to default interval
        time.sleep(API_CALL_INTERVAL)
        print("time check")
        print(time.strftime('%Y-%m-%d %H:%M:%S'))
        print()

if __name__ == "__main__":
    main()
