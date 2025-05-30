d3.json("assets/data/df_plotly.json").then(function(data) {
    // Convertir les dates
    data.forEach(d => {
        d.Date = new Date(d.Date);
        d.ELO = +d.ELO;
    });


        const couleurs = {
    "Roger Federer": "#B3D1FF",   // bleu très clair
    "Novak Djokovic": "#80B3FF",  // bleu ciel
    "Rafael Nadal": "#4D94FF",    // bleu doux
    "David Ferrer": "#1A75FF",    // bleu moyen
    "Richard Gasquet": "#0066FF", // bleu soutenu
    "Andy Murray": "#0052CC",     // bleu classique
    "Tomas Berdych": "#003D99",   // bleu foncé
    "Stan Wawrinka": "#002966",   // bleu très foncé
    "Marin Cilic": "#001A4D",     // bleu nuit
    "Andy Roddick": "#000D33"     // presque noir bleuté
};

    // Définir les joueurs à afficher (top 10)
    const joueurs_freq = {};
    data.forEach(d => {
        joueurs_freq[d.Joueur] = (joueurs_freq[d.Joueur] || 0) + 1;
    });

    const top_winners = Object.entries(joueurs_freq)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([name]) => name);

    // Dates triées
    const filtered_dates = [...new Set(data.map(d => d.Date.getTime()))]
        .sort((a, b) => a - b)
        .map(t => new Date(t))
        .filter((_, i) => i % 7 === 0);

    // Construire les frames
    const frames = filtered_dates.map(date => {
        const frame_data = data.filter(d => d.Date <= date);
        return {
            name: date.toISOString().split("T")[0],
            data: top_winners.map(player => {
                const player_data = frame_data.filter(d => d.Joueur === player);
                return {
                    x: player_data.map(d => d.Date),
                    y: player_data.map(d => d.ELO),
                    mode: "lines",
                    name: player,
                    type: "scatter"

                };
            })
        };
    });






    // Tracer les lignes initiales
    const initial_data = top_winners.map(player => {
        const player_data = data.filter(d => d.Joueur === player);
        return {
            x: player_data.map(d => d.Date),
            y: player_data.map(d => d.ELO),
            mode: "lines",
            line: { shape: "spline" },
            name: player,
            type: "scatter",
            line: {
                shape: "spline",
                color: couleurs[player] || "#cccccc"
            },

        };
    });

    // Layout de la figure
    const layout = {
        title: "Evolution of ELO Ratings of the Top 10 Players (2000–Present)",
        xaxis: {
        title: "Date",
        showgrid: false,         // ❌ pas de grille
        showline: true,          // ✅ garder l’axe
        linecolor: "#0033a0",    // couleur de l’axe X
        tickcolor: "#0033a0",    // couleur des ticks
        color: "#0033a0"         // couleur des labels
    },
    yaxis: {
        title: "ELO",
        showgrid: false,         // ❌ pas de grille
        showline: true,          // ✅ garder l’axe
        linecolor: "#0033a0",    // couleur de l’axe Y
        tickcolor: "#0033a0",
        color: "#0033a0"},
        // 👉 Couleur de fond
    paper_bgcolor: "#fff7f2",  // Couleur externe au graphique (même que ton site)
    plot_bgcolor: "#fff7f2",   // Couleur interne (zone du graphe)

    // 👉 Légende et texte
    font: {
        color: "#333",         // Texte foncé lisible
        family: "sans-serif"
    },
     // 🎯 LÉGENDE personnalisée
        legend: {
      orientation: "h",
      x: 0.5,
      y: -0.5,
      xanchor: "center",
      yanchor: "top",
      bgcolor: "rgba(0,0,0,0)",
      bordercolor: "#fff7f2",
      borderwidth: 1,
      font: {
        color: "#0033a0",
        size: 13
      },
      // 🪄 Ajoute cette ligne pour forcer un wrap
      itemsizing: 'constant',
      tracegroupgap: 5  // espacement entre groupes
    },

        updatemenus: [{
        type: "buttons",
        showactive: false,
        direction: "down",     // vertical (peut être "left" ou "right")
        x: -0.1,               // ⬅️ décale à gauche (0 = bord gauche du graphe)
        y: 1,                  // ⬆️ place en haut du graphe (1 = bord supérieur)

            
        buttons: [ {
                    label: "Play",
                    method: "animate",
                    args: [null, {
                        frame: { duration: 259, redraw: true },
                        fromcurrent: true,
                        transition: { duration: 1000, easing: "cubic-in-out" }
                    }]
                },
                {
                    label: "Pause",
                    method: "animate",
                    args: [[null], {
                        frame: { duration: 0, redraw: false },
                        mode: "immediate"
                    }]
                },
                {
                    label: "Restart",
                    method: "animate",
                    args: [null, {
                        frame: { duration: 250, redraw: true },
                        mode: "immediate",
                        fromcurrent: false
                    }]
                } ],
        font: { color: "#0033a0" },  // boutons blancs
        bgcolor: "#fff7f2",          // même fond que le graphe
        bordercolor: "#fff7f2"
    }],
              

    };

    // Générer la figure
    Plotly.newPlot("graph-atp", initial_data, layout, {responsive: true}).then(() => {
    Plotly.addFrames("graph-atp", frames);
});
});
