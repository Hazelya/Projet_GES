<?php

header('Content-Type: application/json');

if (isset($_POST['depart']) && isset($_POST['arrive'])) { // On vérifie que depart et arrive sont remplies
    // Récupère les adresses saisies
    $depart = escapeshellarg($_POST['depart']);
    $arrive = escapeshellarg($_POST['arrive']);


    // Commande pour exécuter le script Python
    $command = "python ../scriptFusion/calcul.py $depart $arrive";

    // On exécute le script Python et on récupère la sortie
    $output = shell_exec($command);

    if ($output === null) { // si la sortie du script ne vaut rien
        echo json_encode(['error' => 'Erreur lors de l\'exécution du script Python.']);
    } else {
        // On décode le JSON renvoyé par le script Python
        $data = json_decode($output, true);

        if (json_last_error() === JSON_ERROR_NONE) { // On vérifie qu'il n'y a pas d'erreur dans les données
            echo json_encode($data); // On renvoie les données au js
        } else {
            echo json_encode(['error' => 'Les données retournées ne sont pas valides.']);
        }
    }
} else {
    echo json_encode(['error' => 'Revérifier les adresses.']);
}



