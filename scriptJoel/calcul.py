import networkx as nx
import osmnx as ox
from geopy.geocoders import Nominatim
import requests

COUT_PAR_KM = {
    "voiture": 0.15,
    "vélo": 0,
    "marche": 0,
    "moto": 0.12,
}

VITESSE = {
    "voiture": 53,
    "vélo": 15,
    "marche": 5,
    "moto": 43,
}

CARBON = {
    "voiture": "4",  # voiture thermique
    "vélo": "8",     # vélo à assistance électrique
    "marche": "7",   # marche
    "moto": "13",    # moto
}

def distance1(G, route):
    print("Calcul de la distance totale d'un itinéraire...")
    total = 0
    for i in range(len(route) - 1):
        u, v = route[i], route[i + 1]
        if G.has_edge(u, v):
            longueur = G[u][v][0].get("length", 0)
            total += longueur
        else:
            print(f"Pas d'arête entre {u} et {v} dans le graphe")
    return total / 1000 

def get_carbon(mode, distance_km):
    transport_id = CARBON.get(mode)
    url = f"https://impactco2.fr/api/v1/transport?km={distance_km}&transports={transport_id}"
    headers = {"User-Agent": "RoutePlanner/1.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json().get("data", [])
        if data:
            return data[0]["value"]
        else:
            print("Pas de données reçues de l'API")
            return None
    except Exception as e:
        print(f"Erreur avec l'API Impact CO2 : {e}")
        return None

def calcule_prix(distance_km, mode):
    return distance_km * COUT_PAR_KM.get(mode, 0)

def temps_de_trajet(distance_km, mode):
    return (distance_km / VITESSE[mode]) * 60

def geocodage(adresse):
    geolocator = Nominatim(user_agent="myGeocoder")
    try:
        location = geolocator.geocode(adresse)
        return (location.latitude, location.longitude)
    except Exception as e:
        print(f"Erreur de géocodage : {e}")
        return None

def get_route(graph_drive, start_latlng, end_latlng):
    orig_node = ox.nearest_nodes(graph_drive, X=start_latlng[1], Y=start_latlng[0])
    dest_node = ox.nearest_nodes(graph_drive, X=end_latlng[1], Y=end_latlng[0])
    return nx.shortest_path(graph_drive, orig_node, dest_node, method='dijkstra')
