import pickle
import osmnx as ox


def graphmlgraph():
    # Définir la zone et le type de réseau
    place = 'Calvados'
    network_types = ['drive', 'walk', 'bike']

    # Générer et sauvegarder les graphes
    for network_type in network_types:
        graph = ox.graph_from_place(place, network_type=network_type)
        filename = f"graph_{network_type}.graphml"
        ox.save_graphml(graph, filename)  # Sauvegarder au format .graphml
        print(f"{network_type} graph saved to {filename}")

def picklegraph():
    # Convertir les graphes une seule fois et les sauvegarder
    graph_drive = ox.load_graphml("../graphCalvados/graph_drive.graphml")
    graph_walk = ox.load_graphml("../graphCalvados/graph_walk.graphml")

    with open("../graphCalvados/graph_drive.pkl", "wb") as f:
        pickle.dump(graph_drive, f)

    with open("../graphCalvados/graph_walk.pkl", "wb") as f:
        pickle.dump(graph_walk, f)





if __name__ == '__main__':
    typegraph = "pickle"

    if typegraph == "pickle":
        picklegraph()
    elif typegraph == "graphml":
        graphmlgraph()
