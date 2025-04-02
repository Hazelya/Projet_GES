
'use strict';


$('#buttonGES').click((e) => {
    e.preventDefault();

    const form = document.getElementById('adresseForm')
    const formData = new FormData(form);

    // Appel du fichier php pour lancer le script
    fetch('../PHP/calcul.php', {
        method: 'POST',
        body: formData,
    })

        .then(response => response.json())
        .then(data => { // si on récupère bien une info du php
            const results = document.getElementById('resultat');
            results.innerHTML = '';

            if (data.error) { // si l'info est une erreur
                results.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            } else { // si l'info est le resultat
                for (const [key, values] of Object.entries(data)) {
                    results.innerHTML += `
                                <div class="card text-white bg-success mb-3">
                                    <div class="card-body">
                                        <h5 class="card-title" id="vehicule">${key}</h5>
                                        <p class="card-text">
                                        Bilan carbone : ${values.carbone !== null ? values.carbone.toFixed(2) : 'N/A'} kg CO2<br>
                                        Distance : ${values.distance_km.toFixed(2)} km, 
                                        Temps : ${values.temps_min}, 
                                        Coût : ${values.prix.toFixed(2)} euro.
                                        </p>
                                    </div>
                                </div>`;
                }
            }
        })
        .catch(error => { // s'il y a une quelconque erreur liée au fichier
            document.getElementById('resultat').innerHTML = '<div class="alert alert-danger">Une erreur s\'est produite.</div>';
        });
});



$('#buttonCarte').click((e) => {
    e.preventDefault();

    const form = document.getElementById('adresseForm')
    const formData = new FormData(form);

    // Vérifier si le formulaire est vide
    let formIsEmpty = true;
    for (const value of formData.values()) {
        if (value) {
            formIsEmpty = false;
            break;
        }
    }

    // Si le formulaire est vide, ne rien faire
    if (formIsEmpty) {
        return;
    }

    // Appel du fichier php pour lancer le script
    fetch('../PHP/carte.php', {
        method: 'POST',
        body: formData,
    })

        .then(response => response.json())
        .then(data => { // si on récupère bien une info du php
            const results = document.getElementById('resultat');
            results.innerHTML = '';
            results.innerHTML = `<iframe src="../ressources/carteTemporaire.html" width="100%" height="500"></iframe>`;

        })
        .catch(error => { // s'il y a une quelconque erreur liée au fichier
            document.getElementById('resultat').innerHTML = '<div class="alert alert-danger">Une erreur s\'est produite.</div>';
        });
});




/*
//
// Boutton de validation calcul carbonne entre deux adresses
//
document.getElementById('carbonForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    // Appel du fichier php pour lancer le script
    fetch('../PHP/calcul.php', {
        method: 'POST',
        body: formData,
    })

    .then(response => response.json())
    .then(data => { // si on récupère bien une info du php
        const results = document.getElementById('resultat');
        results.innerHTML = '';

        if (data.error) { // si l'info est une erreur
            results.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
        } else { // si l'info est le resultat
            for (const [key, value] of Object.entries(data)) {
                results.innerHTML += `
                                <div class="card text-white bg-success mb-3">
                                    <div class="card-body">
                                        <h5 class="card-title" id="vehicule">${key}</h5>
                                        <p class="card-text">Taux de GES : ${value.toFixed(2)}</p>
                                    </div>
                                </div>`;
            }
        }
    })
    .catch(error => { // s'il y a une quelconque erreur liée au fichier calcul.js
        document.getElementById('resultat').innerHTML = '<div class="alert alert-danger">Une erreur s\'est produite.</div>';
    });
});

*/