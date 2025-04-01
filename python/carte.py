import pickle
import sys
import mpu
import networkx as nx
import osmnx as ox
from geopy.geocoders import Nominatim
import folium

# Package personnel
from packageGES.bus import bus


def heuristic(n1, n2, graph):
    """Heuristique basée sur la distance euclidienne mise à l'échelle pour approximer la distance terrestre"""
    lat1, lon1 = graph.nodes[n1]['y'], graph.nodes[n1]['x']
    lat2, lon2 = graph.nodes[n2]['y'], graph.nodes[n2]['x']

    dist = mpu.haversine_distance((lat1, lon1), (lat2, lon2))
    return dist


def astar(graph, start_latlng, end_latlng) :
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

    shortest_route = astar(graph_drive, start_latlng, end_latlng)

    # --------------- Chemin ---------------------

    with open("../graphCalvados/graph_walk.pkl", "rb") as f:
        graph_walk = pickle.load(f)

    shortest_chemin = astar(graph_walk, start_latlng, end_latlng)

    # --------------- Train ---------------------

    with open("../graphCalvados/graph_train.pkl", "rb") as f:
        graph_train = pickle.load(f)

    shortest_fer = astar(graph_train, start_latlng, end_latlng)

    # --------------- Bus ---------------------

    chemin, infos, coord_depart, coord_arrivee, stop_depart, stop_arrivee = bus(depart, arrive, "carte")

    # --------------- Carte ---------------------

    # Carte Folium
    map_folium = folium.Map(location=start_latlng, zoom_start=13)
    
    legend_html = '''
         <div style="
             position: fixed;
             bottom: 20px;
             right: 20px;
             width: 180px;
             background-color: white;
             border: 1px solid grey;
             border-radius: 5px;
             padding: 10px;
             box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
             font-size: 13px;
             z-index: 9999;
         ">
         <b>Légende</b><br>
         <span style="color:blue;">&#9632;</span> Route<br>
         <span style="color:red;">&#9632;</span> Chemin à pied<br>
         <span style="color:purple;">&#9632;</span> Train<br>
         <span style="color:green;">&#9632;</span> Marcher<br>
         <span style="color:pink;">&#9632;</span> Arrêts
         </div>
    '''
    map_folium.get_root().html.add_child(folium.Element(legend_html))

    route_coords = []
    chemin_coords = []
    train_coords = []

    for node in shortest_route :
        route_coords.append((graph_drive.nodes[node]['y'], graph_drive.nodes[node]['x']))
    for node in shortest_chemin :
        chemin_coords.append((graph_walk.nodes[node]['y'], graph_walk.nodes[node]['x']))
    for node in shortest_fer :
        train_coords.append((graph_train.nodes[node]['y'], graph_train.nodes[node]['x']))

    # Ajouter les lignes (PolyLine)
    folium.PolyLine(route_coords, color='blue', weight=3, opacity=0.7).add_to(map_folium)
    folium.PolyLine(chemin_coords, color='red', weight=3, opacity=0.7).add_to(map_folium)
    folium.PolyLine(train_coords, color='purple', weight=3, opacity=0.7).add_to(map_folium)

    # Tracer à pied de la position réelle au premier arrêt

    folium.PolyLine(locations=[coord_depart, infos[stop_depart]["coord"]], color="green", weight=2.5, opacity=0.7,
                    dash_array="5").add_to(map_folium)

    # Tracer à pied du dernier arrêt à la destination réelle

    folium.PolyLine(locations=[infos[stop_arrivee]["coord"], coord_arrivee], color="green", weight=2.5, opacity=0.7,
                    dash_array="5").add_to(map_folium)

    # Tracer les points du chemin

    chemin_coords = [infos[stop]["coord"] for stop in chemin]

    folium.PolyLine(locations=chemin_coords, color="pink", weight=3, opacity=0.7).add_to(map_folium)

    # Ajouter un marqueur pour chaque arrêt

    for stop in chemin:
        nom = infos[stop]["nom"]
        coord = infos[stop]["coord"]
        folium.CircleMarker(
            location=coord,
            radius=4,
            popup=nom,
            color='pink',
            fill=True,
            fill_color='pink'
        ).add_to(map_folium)

    folium.Marker(start_latlng, popup="Départ").add_to(map_folium)
    folium.Marker(end_latlng, popup="Arrivée").add_to(map_folium)

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


