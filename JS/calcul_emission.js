
'use strict';


$('#buttonGES').click((e) => {
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

    const results = document.getElementById('resultat');
    results.innerHTML = '';
    results.innerHTML = '<div class="alert bg-info mb-3 text-white">Chargement, cela peut prendre quelque seconde.</div>';


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
                let htmlFinal = ` <div align="right">
                                            <img src="../images/legend_pourcentage.png" width="500">
                                          </div> `;
                for (const [key, values] of Object.entries(data)) {
                    let stringResult = `<div class="card bg-success mb-3">
                                        <div class="card-header text-white"> <h4> ${key} </h4> </div>
                                        <div class="card-body">
                
                                            <div class="card border-success mb-3">
                                                <div class="card-body">
                                                    <h6 class="card-title" id="trajetSimple">Trajet simple</h6>
                                                    <p class="card-text">
                                                        Bilan carbone : ${values.carbone !== null ? values.carbone.toFixed(2) : 'N/A'} kg CO2<br>
                                                        Distance : ${values.distance_km.toFixed(2)} km,
                                                        Temps : ${values.temps_min},
                                                        Coût : ${values.prix.toFixed(2)} euro.
                                                    </p> `;
                    if (key !== "Marche" && key !== "Vélo mécanique") {
                        stringResult += `<div class="progress">
                                            <div class="progress-bar progress-bar-striped bg-dark" role="progressbar"
                                                 style="width: ${values.pourcentage_sans_construction}%" aria-valuemin="0"
                                                 aria-valuemax="100"></div>
                                        </div> `;
                    }

                    stringResult += `</div>
                                    </div>
                                        <div class="card border-success mb-3">
                                            <div class="card-body">
                                                <h6 class="card-title" id="trajetAn">Trajet sur 1 an aller-retour</h6>
                                                <p class="card-text">
                                                    Bilan carbone : ${values.carbone_an !== null ? values.carbone_an.toFixed(2) : 'N/A'} kg CO2<br>
                                                    Distance : ${values.distance_km_an.toFixed(2)} km,
                                                    Coût : ${values.prix_an.toFixed(2)} euro.
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                    </div>
                    `;
                    htmlFinal += stringResult;
                }
                results.innerHTML = htmlFinal;
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

    const results = document.getElementById('resultat');
    results.innerHTML = '';
    results.innerHTML = '<div class="alert bg-info mb-3 text-white">Chargement, cela peut prendre quelque seconde.</div>';

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



