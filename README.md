
# Projet GES 

Dans le cadre de notre année académique à l’ISEN, nous avons pour tâcher de réaliser un projet de M1 visant à développer
un logiciel permettant aux utilisateurs de mesurer leur empreinte carbone en fonction de leurs trajets et des modes de 
transport utilisés. En exploitant des données, comme celle de transport.data.gouv.fr, et des outils comme la base de 
données géographiques OSMnx et les bases de données de l’ADEME, l’objectif est de donner aux utilisateurs, des solutions 
modélisées et optimisées en termes de temps, de coût et d’empreinte carbone.

## Explication de l'arborescence : 

### Graph calvados 
Contient le script qui permet de télécharger les graphs
Les graphs seront stocker dans ce même dossier

### Images 
Contient les images, logo, legend ... nécéssaire au design du site

### JS 
Contient le fichier JS qui gére :

    => L'appui des boutons 
    => L'appel du bon fichier PHP 
    => Affichage du résultat du script renvoyer par le PHP

### python 
Contient les script python
Un pour calculer les émissions, le prix, le temps du trajet...
Un pour créer la carte des différents trajets possible

### ressources 
Contient la carte temporaire des trajets qu'on doit afficher

### Hors dossier 
Les deux fichiers HTML du site 


## Comment utiliser le code :

Utiliser le script python dans graphCalvados afin de télécharger les graphes : 
python ./chemin/vers/lefichier/genererSauvegarde.py

Télécharger les librairies nécéssaire : 

    => 
    => pip install git+https://github.com/Hazelya/packageGES.git

Vous n'avez pu qu'a ouvrir le fichier html : index.html
Et profitez du site 






