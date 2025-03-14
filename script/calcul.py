import math
import pickle
import sys
import json
from traceback import print_tb

import networkx as nx
import osmnx as ox
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

import requests

import mpu
import pandas as pd

import time


liste_transport = {
    "Moto": "graph_drive",
    "Voiture thermique": "graph_drive",
    "Scooter et moto légère": "graph_drive",
    "Voiture électrique": "graph_drive",
    "Autocar": "graph_drive",
    "Vélo à assistance électrique": "graph_walk",
    "Trottinette électrique": "graph_walk",
    "Vélo": "graph_walk",
    "Marche": "graph_walk"
}



def heuristic(n1, n2, graph):
    """
    Heurestique de la fonction a-star
    :param n1:
    :param n2:
    :param graph:
    :return:
    """
    lat1, lon1 = graph.nodes[n1]['y'], graph.nodes[n1]['x']
    lat2, lon2 = graph.nodes[n2]['y'], graph.nodes[n2]['x']
    return mpu.haversine_distance((lat1, lon1), (lat2, lon2))

def distance(G, route):
    """
    Calcul la distance en km entre les deux points
    :param G:
    :param route:
    :return:
    """
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
    """
    Récupère est calcul le carbon émis d'un véhicule en particulier
    :param mode:
    :param distance_km:
    :return:
    """
    try:
        # Charger le fichier Excel
        df = pd.read_excel('../ressources/impactCarbone.xlsx')

        # Récupérer les émissions
        emissions = df.loc[df['mode_transport'] == mode, 'emissions']

        if not emissions.empty:
            return (int(emissions.values[0]) / 10) * distance_km
        else:
            print(f"Erreur pour le mode {mode} : non trouvé dans le fichier.")
            return None
    except Exception as e:
        print(f"Erreur avec le fichier excel : {e}")
        return None




def calcule_prix(distance_km, mode):
    """
    Calcul le prix du trajet
    :param distance_km:
    :param mode:
    :return:
    """
    try:
        # Charger le fichier Excel
        df = pd.read_excel('../ressources/impactCarbone.xlsx')

        # Récupérer les émissions
        prix_km = df.loc[df['mode_transport'] == mode, 'prix']

        if not prix_km.empty:
            return float(prix_km.values[0]) * distance_km
        else:
            print(f"Erreur pour le mode {mode} : non trouvé dans le fichier.")
            return None
    except Exception as e:
        print(f"Erreur avec le fichier excel : {e}")
        return None

def temps_de_trajet(distance_km, mode):
    """
    Calcul le temps de trajet
    :param distance_km:
    :param mode:
    :return:
    """
    try:
        # Charger le fichier Excel
        df = pd.read_excel('../ressources/impactCarbone.xlsx')

        # Récupérer les émissions
        vitesse_km = df.loc[df['mode_transport'] == mode, 'vitesse']

        if not vitesse_km.empty:
            heure_decimal = distance_km / int(vitesse_km.values[0])
            # Conversion et formatage simple
            heures = int(heure_decimal)
            minutes = round((heure_decimal - heures) * 60)
            return f"{heures}h{minutes:02d}"
        else:
            print(f"Erreur pour le mode {mode} : non trouvé dans le fichier.")
            return None
    except Exception as e:
        print(f"Erreur avec le fichier excel : {e}")
        return None




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
    Calcul les émissions le prix... pour chaque véhicule entre deux adresses donnés
    :param depart:
    :param arrive:
    :return:
    """

    geolocator = Nominatim(user_agent="myGeocoder")
    start_latlng = geocodage(depart)
    end_latlng = geocodage(arrive)

    tableau = {}

    # On Récupère les deux graphes
    with open("../graphCalvados/graph_drive.pkl", "rb") as f:
        graph_drive = pickle.load(f)

    with open("../graphCalvados/graph_walk.pkl", "rb") as f:
        graph_walk = pickle.load(f)

    # chemin le plus court (A-star)
    route = get_route(graph_drive, start_latlng, end_latlng)
    chemin = get_route(graph_walk, start_latlng, end_latlng)


    # On attribue à chaque moyen de transport le graph qui corresspond puis on les parcours
    for mode, graph in liste_transport.items():
        try:
            # On récupère une par une les information
            if graph == "graph_drive" :
                distance_km = distance(graph_drive, route)
            else:
                distance_km = distance(graph_walk, chemin)

            carbon = get_carbon(mode, distance_km) # API bilan carbone
            cost = calcule_prix(distance_km, mode)
            temps = temps_de_trajet(distance_km, mode)

            nom = mode.encode().decode('unicode_escape')

            # Remplissage du tableau avec les valeurs de chaque mode de transport
            tableau[nom] = {
                "distance_km": distance_km,
                "carbone": carbon,
                "prix": round(cost, 2),
                "temps_min": temps
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
