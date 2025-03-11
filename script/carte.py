import sys
import json

import networkx as nx
import osmnx as ox
import pandas as pd
from geopy.geocoders import Nominatim
import plotly.express as px







def createMap(depart, arrive):

    geolocator = Nominatim(user_agent="myGeocoder")

    # Géocoder l'adresse
    location = geolocator.geocode(depart)
    location_2 = geolocator.geocode(arrive)

    start_latlng = (location.latitude, location.longitude)
    end_latlng = (location_2.latitude, location_2.longitude)

    # ---------------- Route --------------------

    graph_drive = ox.load_graphml("../graphCalvados/graph_drive.graphml")

    # Trouver le nœud le plus proche de l'emplacement de départ
    orig_node = ox.nearest_nodes(graph_drive, X=start_latlng[1],Y=start_latlng[0])
    dest_node = ox.nearest_nodes(graph_drive, X=end_latlng[1], Y=end_latlng[0])

    shortest_route = nx.shortest_path(graph_drive, orig_node, dest_node, method='dijkstra')

    # --------------- Chemin ---------------------

    graph_walk = ox.load_graphml("../graphCalvados/graph_walk.graphml")

    # find the nearest node to the start location
    orig_node = ox.nearest_nodes(graph_walk, X=start_latlng[1], Y=start_latlng[0])  # find the nearest node to the end location
    dest_node = ox.nearest_nodes(graph_walk, X=end_latlng[1], Y=end_latlng[0])

    shortest_chemin = nx.shortest_path(graph_walk, orig_node, dest_node, method='dijkstra')

    # ------------- DataFrame --------------------

    # Initialiser une liste pour stocker les coordonnées des nœuds
    line_nodes = []

    # Parcourir tous les nœuds du chemin le plus court
    for node in shortest_route:
        # Récupérer la latitude et la longitude du nœud
        latitude = graph_drive.nodes[node]['y']
        longitude = graph_drive.nodes[node]['x']
        network = 'Voiture Thermique, Voiture électrique, Moto, Scooter ou moto légère'

        # Ajouter les coordonnées sous forme de tuple (latitude, longitude) à la liste
        line_nodes.append((network, latitude, longitude))

    for node in shortest_chemin:
        # Récupérer la latitude et la longitude du nœud
        latitude = graph_walk.nodes[node]['y']
        longitude = graph_walk.nodes[node]['x']
        network = 'Vélo (ou trottinette) à assistance électrique, Vélo ou marche'

        # Ajouter les coordonnées sous forme de tuple (latitude, longitude) à la liste
        line_nodes.append((network, latitude, longitude))

    # Convertir les coordonnées en DataFrame pour Plotly Express
    line_df = pd.DataFrame(line_nodes, columns=['network', 'latitude', 'longitude'])

    # ----------------- Carte ---------------------

    # Afficher le chemin avec Plotly Express
    fig = px.line_mapbox(
        line_df,
        lat='latitude',
        lon='longitude',
        color='network',
        title="Chemin le plus court",
        mapbox_style="open-street-map",
        zoom=12
    )

    # --------------- Enregistrement --------------

    # Sauvegarder en tant que fichier HTML
    fig.write_html("carte.html")





if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py <depart> <arrive>")
        sys.exit(1)

    depart = sys.argv[1]
    arrive = sys.argv[2]

    createMap(depart, arrive)


