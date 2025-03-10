import math
import sys
import json
from traceback import print_tb

import networkx as nx
import osmnx as ox
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

import requests
import mpu



def calcul(depart, arrive):

    # Initialiser le géocodeur
    geolocator = Nominatim(user_agent="myGeocoder")

    # Trouver les adresses
    location = geolocator.geocode(str(depart))
    location_2 = geolocator.geocode(str(arrive))

    # Tutple de la latitude et longitude des adresse
    start_latlng = (location.latitude, location.longitude)
    end_latlng = (location_2.latitude, location_2.longitude)

    tableau = {} # Tableau qui contient les infos des transports (dictionnaire)


    # Appelle de fonction selon le type de trajet (route, chemin...)
    route(start_latlng, end_latlng, tableau)
    walk(start_latlng, end_latlng, tableau)


    # trie le tableau dans l'ordre croissant de taux de GES
    sorted_tableau = dict(sorted(tableau.items(), key=lambda item:item[1]))

    # Réponse du script (sera récupéré par le php)
    print(json.dumps(sorted_tableau, ensure_ascii=False, indent=4))



def heuristic(n1, n2, graph):
    """Heuristique basée sur la distance euclidienne mise à l'échelle pour approximer la distance terrestre"""
    lat1, lon1 = graph.nodes[n1]['y'], graph.nodes[n1]['x']
    lat2, lon2 = graph.nodes[n2]['y'], graph.nodes[n2]['x']

    dist = mpu.haversine_distance((lat1, lon1), (lat2, lon2))
    return dist



def route(start_latlng, end_latlng, tableau):
    # Ouvre le graph des routes pré enregistrés
    graph_drive = ox.load_graphml("../graphCalvados/graph_drive.graphml")

    # Trouver le nœud le plus proche de l'emplacement de départ
    orig_node = ox.nearest_nodes(graph_drive, X=start_latlng[1],Y=start_latlng[0])
    dest_node = ox.nearest_nodes(graph_drive, X=end_latlng[1], Y=end_latlng[0])

    # Calcul le chemin le plus court
    # Utilisation de A*
    shortest_route = nx.astar_path(graph_drive, orig_node, dest_node,
                                    heuristic=lambda n1, n2: heuristic(n1, n2, graph_drive))

    # Calcul de la distance totale du trajet (en mètres)
    total_distance = 0
    for i in range(len(shortest_route) - 1):
        edge_data = graph_drive.get_edge_data(shortest_route[i], shortest_route[i + 1])
        if edge_data:  # Vérification que l'arête existe

            # Certaines arêtes peuvent avoir plusieurs "versions" (multi-graph)
            distance = min(d['length'] for d in edge_data.values())

            total_distance += distance

    # Conversion en kilomètres
    shortest_route_km = total_distance / 1000

    transport = ['4', '5', '12', '13'] # Id des transports qui nous intéressent dans l'api

    for i in transport : # Pour chaque id de transports
        # Demande à l'api de calculer le GES
        url = "https://impactco2.fr/api/v1/transport?km=" + str(shortest_route_km) + "&transports=" + str(i)
        reponse = requests.get(url) # Lancement de la requète
        content = reponse.json()
        data = content['data']

        # Correction de l'encodage avant ajout dans le tableau
        name = data[0]['name'].encode().decode('unicode_escape')
        tableau.update({name : data[0]['value']}) # ajout du nouveau transport

def walk(start_latlng, end_latlng, tableau):
    # Ouvre le graph des chemins pré enregistrés
    graph_walk = ox.load_graphml("../graphCalvados/graph_walk.graphml")

    # Trouver le nœud le plus proche de l'emplacement de départ
    orig_node = ox.nearest_nodes(graph_walk, X=start_latlng[1],Y=start_latlng[0])
    dest_node = ox.nearest_nodes(graph_walk, X=end_latlng[1], Y=end_latlng[0])

    # Calcul le chemin le plus court
    # Utilisation de A*
    shortest_route = nx.astar_path(graph_walk, orig_node, dest_node,
                                   heuristic=lambda n1, n2: heuristic(n1, n2, graph_walk))


    # Calcul de la distance totale du trajet (en mètres)
    total_distance = 0
    for i in range(len(shortest_route) - 1):
        edge_data = graph_walk.get_edge_data(shortest_route[i], shortest_route[i + 1])
        if edge_data:  # Vérification que l'arête existe

            # Certaines arêtes peuvent avoir plusieurs "versions" (multi-graph)
            distance = min(d['length'] for d in edge_data.values())

            total_distance += distance

    # Conversion en kilomètres
    shortest_chemin_km = total_distance / 1000

    transport = ['7', '8'] # Id des transports qui nous intéressent dans l'api

    for i in transport :
        # Demande à l'api de calculer le GES
        url = "https://impactco2.fr/api/v1/transport?km=" + str(shortest_chemin_km) + "&transports=" + str(i)
        reponse = requests.get(url)
        content = reponse.json()
        data = content['data']

        # Correction de l'encodage avant ajout dans le tableau
        name = data[0]['name'].encode().decode('unicode_escape')
        tableau.update({name : data[0]['value']})



if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py <depart> <arrive>")
        sys.exit(1)

    depart = sys.argv[1]
    arrive = sys.argv[2]

    calcul(depart, arrive)


