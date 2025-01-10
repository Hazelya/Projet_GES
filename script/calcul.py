import sys
import json

import networkx as nx
import osmnx as ox
from geopy.geocoders import Nominatim

import requests



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



def route(start_latlng, end_latlng, tableau):
    # Ouvre le graph des routes pré enregistrés
    graph_drive = ox.load_graphml("../graphCalvados/graph_drive.graphml")

    # Trouver le nœud le plus proche de l'emplacement de départ
    orig_node = ox.nearest_nodes(graph_drive, X=start_latlng[1],Y=start_latlng[0])
    dest_node = ox.nearest_nodes(graph_drive, X=end_latlng[1], Y=end_latlng[0])

    # Calcul le chemin le plus court
    shortest_route_length = nx.shortest_path_length(graph_drive, orig_node, dest_node, weight='length', method='dijkstra') # 'length' renvoie le chemin en metre
    shortest_route_km = shortest_route_length / 1000 # convertir en km

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

    shortest_route_length = nx.shortest_path_length(graph_walk, orig_node, dest_node, weight='length', method='dijkstra')
    shortest_route_km = shortest_route_length / 1000

    transport = ['7', '8'] # Id des transports qui nous intéressent dans l'api

    for i in transport :
        # Demande à l'api de calculer le GES
        url = "https://impactco2.fr/api/v1/transport?km=" + str(shortest_route_km) + "&transports=" + str(i)
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


