
# Projet GES 

Dans le cadre de notre année académique à l’ISEN, nous avons pour tâche de réaliser un projet de M1 visant à développer
un logiciel permettant aux utilisateurs de mesurer leur empreinte carbone en fonction de leurs trajets et des modes de 
transport utilisés. En exploitant des données, comme celle de transport.data.gouv.fr, et des outils comme la base de 
données géographique OSMnx et les bases de données de l’ADEME, l’objectif est de donner aux utilisateurs, des solutions 
modélisées et optimisées en termes de temps, de coût et d’empreinte carbone.

## Explication de l'arborescence : 

### Graphes Calvados 
Contient le script qui permet de télécharger les graphes.
Ils seront stockés dans ce même dossier.

### Images 
Contient les images, logo, légende... nécessaires au design du site

### JS 
Contient le fichier JS qui gère :

    => L'appui des boutons 
    => L'appel du bon fichier PHP 
    => Affichage du résultat du script renvoyé par le PHP

### Python 
Contient les scripts Python.
Un pour calculer les émissions, le prix, le temps du trajet...
Un pour créer la carte des différents trajets possible.

### ressources 
Contient la carte temporaire des trajets qu'on doit afficher.

### Hors dossier 
Les deux fichiers HTML du site.


## Comment utiliser le code :

Utiliser le script python dans graphCalvados afin de télécharger les graphes (si c'est pas le cas) : 
python ./chemin/vers/lefichier/genererSauvegarde.py

Télécharger les librairies nécessaires : 

    => pickle
    => sys
    => json
    => mpu
    => networkx
    => pickle
    => osmnx
    => geopy.geocoders.Nominatim
    => pandas
    => plotly.express
    => folium
    => pip install git+https://github.com/Hazelya/packageGES.git

Vous n'avez pouvez ouvrir le fichier HTML index.html dans une page web.
Et profitez du site.






