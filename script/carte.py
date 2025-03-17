import pickle
import sys
import json

import mpu
import networkx as nx
import osmnx as ox
import pandas as pd
from geopy.geocoders import Nominatim
import plotly.express as px

import folium




def heuristic(n1, n2, graph):
    """Heuristique basée sur la distance euclidienne mise à l'échelle pour approximer la distance terrestre"""
    lat1, lon1 = graph.nodes[n1]['y'], graph.nodes[n1]['x']
    lat2, lon2 = graph.nodes[n2]['y'], graph.nodes[n2]['x']

    dist = mpu.haversine_distance((lat1, lon1), (lat2, lon2))
    return dist




def createMap(depart, arrive):
    geolocator = Nominatim(user_agent="myGeocoder")

    # Géocoder l'adresse
    location = geolocator.geocode(depart)
    location_2 = geolocator.geocode(arrive)

    start_latlng = (location.latitude, location.longitude)
    end_latlng = (location_2.latitude, location_2.longitude)

    # ---------------- Route --------------------

    with open("../graphCalvados/graph_drive.pkl", "rb") as f:
        graph_drive = pickle.load(f)

    # Trouver le nœud le plus proche de l'emplacement de départ
    orig_node = ox.nearest_nodes(graph_drive, X=start_latlng[1], Y=start_latlng[0])
    dest_node = ox.nearest_nodes(graph_drive, X=end_latlng[1], Y=end_latlng[0])

    shortest_route = nx.astar_path(graph_drive, orig_node, dest_node,
                                   heuristic=lambda n1, n2: heuristic(n1, n2, graph_drive))

    # --------------- Chemin ---------------------

    with open("../graphCalvados/graph_walk.pkl", "rb") as f:
        graph_walk = pickle.load(f)

    # find the nearest node to the start location
    orig_node = ox.nearest_nodes(graph_walk, X=start_latlng[1],
                                 Y=start_latlng[0])  # find the nearest node to the end location
    dest_node = ox.nearest_nodes(graph_walk, X=end_latlng[1], Y=end_latlng[0])

    shortest_chemin = nx.astar_path(graph_walk, orig_node, dest_node,
                                    heuristic=lambda n1, n2: heuristic(n1, n2, graph_walk))
    # Carte Folium
    map_folium = folium.Map(location=start_latlng, zoom_start=13)

    route_coords = []
    chemin_coords = []

    for node in shortest_route :
        route_coords.append((graph_drive.nodes[node]['y'], graph_drive.nodes[node]['x']))
    for node in shortest_chemin :
        chemin_coords.append((graph_walk.nodes[node]['y'], graph_walk.nodes[node]['x']))

    # Ajouter les lignes (PolyLine)
    folium.PolyLine(route_coords, color='blue', weight=3, opacity=0.7).add_to(map_folium)
    folium.PolyLine(chemin_coords, color='green', weight=3, opacity=0.7).add_to(map_folium)

    folium.Marker(start_latlng, popup="Départ").add_to(map_folium)
    folium.Marker(end_latlng, popup="Arrivée", color='red').add_to(map_folium)

    # Sauvegarde
    map_folium.save("../ressources/carteTemporaire.html")
    print("Carte créée")




if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py <depart> <arrive>")
        sys.exit(1)

    depart = sys.argv[1]
    arrive = sys.argv[2]

    createMap(depart, arrive)


