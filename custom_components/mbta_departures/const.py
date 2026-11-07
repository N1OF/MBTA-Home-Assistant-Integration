"""Constants for MBTA Departures."""
DOMAIN = "mbta_departures"
STATIONS = {"place-sstat": "South Station", "place-north": "North Station"}
SERVICES = {
    "place-sstat": {"red": ("Red Line", ("Red",)), "silver": ("Silver Line", ("741", "742", "743", "751", "749")), "rail": ("Commuter Rail", ())},
    "place-north": {"orange": ("Orange Line", ("Orange",)), "green": ("Green Line", ("Green-B", "Green-C", "Green-D", "Green-E")), "rail": ("Commuter Rail", ())},
}
