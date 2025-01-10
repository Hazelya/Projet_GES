import osmnx as ox

# Définir la zone et le type de réseau
place = 'Calvados'
network_types = ['drive', 'walk', 'bike']

# Générer et sauvegarder les graphes
for network_type in network_types:
    graph = ox.graph_from_place(place, network_type=network_type)
    filename = f"graph_{network_type}.graphml"
    ox.save_graphml(graph, filename)  # Sauvegarder au format .graphml
    print(f"{network_type} graph saved to {filename}")