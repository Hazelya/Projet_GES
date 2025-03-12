import math
import sys
import json
from traceback import print_tb

import networkx as nx
import osmnx as ox
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

import requests

import time
import mpu

# Constantes
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

def heuristic(n1, n2, graph):
    lat1, lon1 = graph.nodes[n1]['y'], graph.nodes[n1]['x']
    lat2, lon2 = graph.nodes[n2]['y'], graph.nodes[n2]['x']
    return mpu.haversine_distance((lat1, lon1), (lat2, lon2))

def distance1(G, route):
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
        return data[0]["value"] if data else None
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

def get_route(graph, start_latlng, end_latlng):
    """
    Retourne le chemin le plus court selon le graph (route, chemin...)
    :param graph:
    :param start_latlng:
    :param end_latlng:
    :return:
    """
    orig_node = ox.nearest_nodes(graph, X=start_latlng[1], Y=start_latlng[0])
    dest_node = ox.nearest_nodes(graph, X=end_latlng[1], Y=end_latlng[0])
    return nx.astar_path(graph, orig_node, dest_node, heuristic=lambda n1, n2: heuristic(n1, n2, graph))

def calcul(depart, arrive):
    """
    Calcul pour chaque type de transport, le bilan carbone, le prix, le temps...
    :param depart:
    :param arrive:
    :return:
    """
    geolocator = Nominatim(user_agent="myGeocoder")
    start_latlng = geocodage(depart)
    end_latlng = geocodage(arrive)

    tableau = {}

    # On Récupère les deux graphes
    graph_drive = ox.load_graphml("../graphCalvados/graph_drive.graphml")
    graph_walk = ox.load_graphml("../graphCalvados/graph_walk.graphml")

    # On attribue à chaque moyen de transport le graph qui corresspond puis on les parcours
    for mode, graph in {"voiture": graph_drive, "moto": graph_drive, "vélo": graph_walk, "marche": graph_walk}.items():
        try:
            # On récupère une par une les information
            route = get_route(graph, start_latlng, end_latlng) # chemin le plus court (A-star)
            distance_km = distance1(graph, route)
            carbon = get_carbon(mode, distance_km) # API bilan carbone
            cost = calcule_prix(distance_km, mode)
            time = temps_de_trajet(distance_km, mode)

            mode = mode.encode().decode('unicode_escape') # pour l'encodage des noms vélo (exemple : problème avec le é)

            # Remplissage du tableau avec les valeurs de chaque mode de transport
            tableau[mode] = {
                "distance_km": distance_km,
                "carbone": carbon,
                "prix": cost,
                "temps_min": time
            }
        except Exception as e:
            # Si on capte une erreur
            print(f"Erreur pour le mode {mode} : {e}")


    # Réponse du script (sera récupéré par le php)
    print(json.dumps(tableau, ensure_ascii=False, indent=4))
    sys.stdout.flush()  # Pour être sûr que PHP reçoive tout


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py <depart> <arrive>")
        sys.exit(1)

    depart = sys.argv[1]
    arrive = sys.argv[2]

    calcul(depart, arrive)
