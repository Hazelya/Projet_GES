import os
import pickle
import osmnx as ox


def graphmlgraph():
    """
    Generer les graphml
    :return:
    """
    # Définir la zone et le type de réseau
    place = 'Calvados, France'
    network_types = ['drive', 'walk']

    # Générer et sauvegarder les graphes
    for network_type in network_types:
        graph = ox.graph_from_place(place, network_type=network_type)
        filename = f"graph_{network_type}.graphml"
        ox.save_graphml(graph, filename)  # Sauvegarder au format .graphml
        print(f"{network_type} graph saved to {filename}")

    # générer et sauvegarder le graph du train
    graph = ox.graph_from_place(place, network_type="all", custom_filter='["railway"]')
    filename = f"graph_train.graphml"
    ox.save_graphml(graph, filename)  # Sauvegarder au format .graphml
    print(f"Train graph saved to {filename}")


def picklegraph():
    """
    Transforme les graphml en pickle
    :return:
    """
    network_types = ['drive', 'walk', 'train']

    for network_type in network_types:
        # Charger le graph
        filename = f"graph_{network_type}.graphml"
        graph = ox.load_graphml(filename)

        # Passage au format pickle
        filename = f"graph_{network_type}.pkl"
        with open(filename, "wb") as f:
            pickle.dump(graph, f)


def removegraphml():
    """
    Supprime les graphml
    :return:
    """
    network_types = ['drive', 'walk', 'train']

    for network_type in network_types:
        filename = f"graph_{network_type}.graphml"
        try:
            os.remove(filename)
            print(f"File '{filename}' deleted successfully.")

        except FileNotFoundError: print(f"File '{filename}' not found.")



if __name__ == '__main__':

    graphmlgraph()
    picklegraph()
    removegraphml()
