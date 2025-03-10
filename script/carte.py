import plotly.express as px
import pandas as pd
from calcul import distance1, get_carbon, calcule_prix, temps_de_trajet, geocodage, get_route
import sys
import osmnx as ox

def afficher_carte(shortest_route, graph_drive, mode):
    line_nodes = []

    for node in shortest_route:
        latitude = graph_drive.nodes[node]['y']
        longitude = graph_drive.nodes[node]['x']
        vehicules = f'{mode}'
        line_nodes.append((vehicules, latitude, longitude))

    line_df = pd.DataFrame(line_nodes, columns=['Mode de transport', 'latitude', 'longitude'])

    fig = px.line_mapbox(
        line_df,
        lat='latitude',
        lon='longitude',
        color='Mode de transport',
        mapbox_style="open-street-map",
        zoom=12
    )
    fig.show()

    fig.write_html("carteTemporaire.html")

def createMAP(depart, arrive, mode):
    start_latlng = geocodage(depart)
    end_latlng = geocodage(arrive)

    graph_drive_path = "/Users/joelmwemba/Desktop/Teste3/projet/Calvados.graphml"
    graph_drive = ox.load_graphml(graph_drive_path)

    shortest_route = get_route(graph_drive, start_latlng, end_latlng)
    distance_km = distance1(graph_drive, shortest_route)
    prix = calcule_prix(distance_km, mode)
    temps_trajet = temps_de_trajet(distance_km, mode)
    impact_carbon = get_carbon(mode, distance_km)

    afficher_carte(shortest_route, graph_drive, mode)

    print("\n========== Résultats ==========")
    print(f"Mode de transport: {mode.capitalize()}")
    print(f"Distance: {distance_km:.2f} km")
    print(f"Temps estimé: {temps_trajet:.2f} minutes")
    print(f"Coût estimé: {prix:.2f} €")
    print(f"Impact Carbone: {impact_carbon:.2f} Kg CO2e")

if __name__ == '__main__':
    #php
    #if len(sys.argv) != 4:
        ##sys.exit(1)
    #depart = sys.argv[1]
    #arrive = sys.argv[2]
    #mode = sys.argv[3]
    #createMAP(depart, arrive, mode)

    #vscode
    #depart = "Caen"
    #arrive = "Ouistreham"
    #mode = "voiture"  
    #createMAP(depart, arrive, mode)
