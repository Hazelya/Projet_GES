<?php

header('Content-Type: application/json');

if (isset($_POST['depart']) && isset($_POST['arrive'])) { // On vérifie que depart et arrive sont remplies
    // Récupère les adresses saisies
    $depart = escapeshellarg($_POST['depart']);
    $arrive = escapeshellarg($_POST['arrive']);

    // Commande pour exécuter le script Python
    $command = "python ../script/carte.py $depart $arrive";

    // On exécute le script Python et on récupère la sortie
    $output = shell_exec($command);
    if ($output === null) { // si la sortie du script ne vaut rien
        echo json_encode(['error' => 'Erreur lors de l\'exécution du script Python.']);
    } else {
        echo $output;
    }

} else {
    echo json_encode(['error' => 'Revérifier les adresses.']);
}






