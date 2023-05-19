import math


def locator_distance(locator1, locator2):
    """By: ChatGP"""
    lat1, lon1 = locator_to_coordinates(locator1)
    lat2, lon2 = locator_to_coordinates(locator2)

    # Convert latitude and longitude to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Earth radius in kilometers
    earth_radius = 6371

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = earth_radius * c

    return distance


def locator_to_coordinates(locator):
    """By: ChatGP"""
    A = [ord(char) for char in locator]

    # Extract longitude values
    lon1 = (A[0] - 65) * 20 - 180
    lon2 = (A[2] - 65) * 2
    lon3 = (A[4] - 65) / 12

    # Extract latitude values
    lat1 = (A[1] - 65) * 10 - 90
    lat2 = (A[3] - 48)
    lat3 = (A[5] - 64.5) / 24

    # Calculate final latitude and longitude
    lat = lat1 + lat2 + lat3
    lon = lon1 + lon2 + lon3

    return lat, lon

