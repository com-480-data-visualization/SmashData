
const buttonPanel = document.querySelector('.button-panel'); // Conteneur des boutons
let currentIndex = 0;

// Fonction pour mettre à jour le contenu dynamiquement
function updateContent(index) {
    const buttons = document.querySelectorAll('.button-panel .btn'); // Liste des boutons
    const button = buttons[index];

    const title = button.getAttribute('data-title') || button.textContent;
    const image = button.getAttribute('data-image');
    const text = button.getAttribute('data-text');

    // Référence aux éléments dynamiques
    const contentImage = document.getElementById('content-image');
    const contentTitle = document.getElementById('content-title');
    const contentText = document.getElementById('content-text');

    // Ajouter la classe fade-out pour l'animation
    contentImage.classList.add('fade-out');
    contentTitle.classList.add('fade-out');
    contentText.classList.add('fade-out');

    // Mettre à jour le contenu après l'animation
    setTimeout(() => {
        contentTitle.textContent = title;
        contentImage.src = image;
        contentText.textContent = text;

        // Retirer les animations
        contentImage.classList.remove('fade-out');
        contentTitle.classList.remove('fade-out');
        contentText.classList.remove('fade-out');
    }, 500);

    // Mettre à jour les classes actives
    buttons.forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
}

// Event delegation pour gérer les clics sur les boutons
buttonPanel.addEventListener('click', (event) => {
    const clickedButton = event.target.closest('.btn'); // Vérifie si un bouton a été cliqué
    if (clickedButton) {
        const buttons = Array.from(buttonPanel.querySelectorAll('.btn'));
        currentIndex = buttons.indexOf(clickedButton);
        updateContent(currentIndex);
    }
});

// Fonction pour faire défiler automatiquement les boutons
function autoCycleButtons() {
    setInterval(() => {
        const buttons = document.querySelectorAll('.button-panel .btn');
        currentIndex = (currentIndex + 1) % buttons.length; // Passer au bouton suivant
        updateContent(currentIndex);
    }, 10000); // Change toutes les 10secondes
}

// Initialisation
updateContent(currentIndex);
autoCycleButtons();
