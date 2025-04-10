import pickle
import sys
import json

import networkx as nx
import osmnx as ox
from geopy.geocoders import Nominatim

import mpu

# Package personnel
from packageGES.calcul_ges import calcul_emission, calcul_prix, calcul_temps
from packageGES.bus import bus

liste_transport = {
    "Moto thermique": "graph_drive",
    "Voiture thermique": "graph_drive",
    "Covoiturage thermique (1 passager)": "graph_drive",
    "Covoiturage thermique (2 passagers)": "graph_drive",
    "Covoiturage thermique (3 passagers)": "graph_drive",
    "Covoiturage thermique (4 passagers)": "graph_drive",
    "Scooter ou moto légère thermique": "graph_drive",
    "Voiture électrique": "graph_drive",
    "Covoiturage électrique (1 passager)": "graph_drive",
    "Covoiturage électrique (2 passagers)": "graph_drive",
    "Covoiturage électrique (3 passagers)": "graph_drive",
    "Covoiturage électrique (4 passagers)": "graph_drive",
    "TER": "graph_train",
    "Autocar thermique": "graph_drive",
    "Vélo à assistance électrique": "graph_walk",
    "Trottinette à assistance électrique": "graph_walk",
    "RER ou Transilien": "graph_train",
    "Intercités": "graph_train",
    "Métro": "graph_train",
    "Tramway": "graph_train",
    "TGV": "graph_train",
    "Vélo mécanique": "graph_walk",
    "Marche": "graph_walk",
    # Toujours mettre les "graph_bus" à la fin
    "Bus thermique": "graph_bus"
}





def heuristic(n1, n2, graph):
    """
    Heurestique de la fonction a-star
    :param n1:
    :param n2:
    :param graph:
    :return:
    """
    # On récupère la latitude et la longitude du point de départ et d'arrivé
    lat1, lon1 = graph.nodes[n1]['y'], graph.nodes[n1]['x']
    lat2, lon2 = graph.nodes[n2]['y'], graph.nodes[n2]['x']
    # On applique haversine grâce à la librairie mpu
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



def geocodage(adresse):
    """
    Récupère la latitude et la longitude d'une adresse
    :param adresse:
    :return:
    """
    geolocator = Nominatim(user_agent="myGeocoder")
    try:
        location = geolocator.geocode(adresse)
        return (location.latitude, location.longitude)
    except Exception as e:
        print(f"Erreur de géocodage : {e}")
        return None



def shortest_path(graph, start_latlng, end_latlng):
    """
    Retourne le chemin le plus court selon le graph (route, chemin...)
    :param graph:
    :param start_latlng:
    :param end_latlng:
    :return:
    """
    orig_node = ox.nearest_nodes(graph, X=start_latlng[1], Y=start_latlng[0]) # le noeud dans le graph le plus proche du point de départ
    dest_node = ox.nearest_nodes(graph, X=end_latlng[1], Y=end_latlng[0]) # le noeud dans le graph le plus proche du point d'arrivée

    # On applique A-Star grâce à la librairie networkx
    return nx.astar_path(graph, orig_node, dest_node, heuristic=lambda n1, n2: heuristic(n1, n2, graph))



def calcul(depart, arrive, jourTeletravail):
    """
    Calcul les émissions le prix... pour chaque véhicule entre deux adresses donnés
    :param depart:
    :param arrive:
    :return:
    """

    geolocator = Nominatim(user_agent="myGeocoder")
    # Récupération lat et lng des adresses de l'utilisateur
    start_latlng = geocodage(depart)
    end_latlng = geocodage(arrive)

    tableau = {} # Tableau contenant le résultat

    # On Récupère les graphes
    with open("../graphCalvados/graph_drive.pkl", "rb") as f:
        graph_drive = pickle.load(f)

    with open("../graphCalvados/graph_walk.pkl", "rb") as f:
        graph_walk = pickle.load(f)

    with open("../graphCalvados/graph_train.pkl", "rb") as f:
        graph_train = pickle.load(f)


    # chemin le plus court (A-star) pour chaque graph
    route = shortest_path(graph_drive, start_latlng, end_latlng)
    chemin = shortest_path(graph_walk, start_latlng, end_latlng)
    fer = shortest_path(graph_train, start_latlng, end_latlng)


    # On attribue à chaque moyen de transport le graph qui corresspond puis on les parcours
    for mode, graph in liste_transport.items():
        try:
            # la distance n'est pas la même selon le graph
            if graph == "graph_drive" :
                distance_km = distance(graph_drive, route)
            elif graph == "graph_train" :
                distance_km = distance(graph_train, fer)
            elif graph == "graph_walk" :
                distance_km = distance(graph_walk, chemin)
                #distance_km, distance_trajet, chemin = bus(depart, arrive, "calcul")
            else:
                result = bus(depart, arrive, "calcul")
                if result is None:
                    raise ValueError(f"La fonction bus() n'a rien renvoyé pour {depart} → {arrive}")
                distance_km, distance_trajet, chemin = result

            # On récupère une par une les informations (fonction de notre propre package).
            emission_km, pourcentage_sans_construction = calcul_emission(mode, distance_km)
            cost = calcul_prix(distance_km, mode)

            if graph == "graph_bus" :
                temps_bus = calcul_temps(distance_km, mode)
                temps_marche = calcul_temps((distance_trajet-distance_km), "Marche")
                temps = temps_bus + " de bus et " + temps_marche + " de marche"
                distance_km = distance_trajet # Manip pour quand on va le mettre dans le tableau
            else :
                temps = calcul_temps(distance_km, mode)

            nom = mode.encode().decode('unicode_escape') # decodage + encodage pour les caractères spéciaux dans le nom

            # Calcul pour 1 an de trajet travail
            nbr_jour = 218 - (int(jourTeletravail) * round(218/5))# 218 chiffre du gouvernement
            distance_km_an = distance_km * nbr_jour

            emission_km_an, _ = calcul_emission(mode, distance_km_an)
            cost_an = calcul_prix(distance_km_an, mode)

            # Remplissage du tableau avec les valeurs de chaque mode de transport
            tableau[nom] = {
                "distance_km": distance_km,
                "carbone": emission_km,
                "prix": round(cost, 2),
                "temps_min": temps,
                "pourcentage_sans_construction": pourcentage_sans_construction,

                "distance_km_an" : distance_km_an,
                "carbone_an" : emission_km_an,
                "prix_an" : round(cost_an, 2),
            }
        except Exception as e:
            # Si on capte une erreur
            print(f"Erreur pour le mode {mode} : {e}")

    # on trie le tableau du plus petit rejet de CO2 au plus grand
    sorted_tableau = dict(sorted(tableau.items(), key=lambda item: item[1]['carbone']))

    # Réponse du script (sera récupéré par le php)
    print(json.dumps(sorted_tableau, ensure_ascii=False, indent=4))
    sys.stdout.flush()  # Pour être sûr que PHP reçoive tout


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python script.py <depart> <arrive>")
        sys.exit(1)

    # Demande départ et arrivé
    depart = sys.argv[1]
    arrive = sys.argv[2]
    jourTeletravail = sys.argv[3]

    calcul(depart, arrive, jourTeletravail)
