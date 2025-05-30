d3.json("assets/data/df_plotly_wta.json").then(function(data) {
    // ✅ Convertir les dates et champs
    data.forEach(d => {
        d.Date = new Date(d.date);     
        d.ELO = +d.elo;
        d.Joueur = d.player;
    });

    // ✅ Couleurs en nuances de rouge (déplacé ici)
    const couleurs = {
        "Jankovic J.": "#FFCCCC",     // rouge très clair
        "Williams S.": "#FF9999",     // rose rouge doux
        "Kuznetsova S.": "#FF6666",   // rouge saumon
        "Azarenka V.": "#FF4D4D",     // rouge clair
        "Radwanska A.": "#FF3333",    // rouge franc
        "Sharapova M.": "#FF1A1A",    // rouge vif
        "Wozniacki C.": "#E60000",    // rouge soutenu
        "Kerber A.": "#CC0000",       // rouge foncé
        "Kvitova P.": "#990000",      // bordeaux
        "Halep S.": "#660000"         // rouge très foncé
    };

    // ✅ Définir les joueurs à afficher (top 10 les plus fréquents)
    const joueurs_freq = {};
    data.forEach(d => {
        joueurs_freq[d.Joueur] = (joueurs_freq[d.Joueur] || 0) + 1;
    });

    const top_winners = Object.entries(joueurs_freq)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
        .map(([name]) => name);

    // ✅ Extraire et trier les dates uniques
    const filtered_dates = [...new Set(data.map(d => d.Date.getTime()))]
        .sort((a, b) => a - b)
        .map(t => new Date(t));

    // ✅ Générer les frames pour l’animation
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
                    type: "scatter",
                    line: {
                        shape: "spline",
                        color: couleurs[player] || "#cccccc"
                    }
                };
            })
        };
    });

    // ✅ Tracer les données initiales
    const initial_data_wta = top_winners.map(player => {
        const player_data = data.filter(d => d.Joueur === player);
        return {
            x: player_data.map(d => d.Date),
            y: player_data.map(d => d.ELO),
            mode: "lines",
            name: player,
            type: "scatter",
            line: {
                shape: "spline",
                color: couleurs[player] || "#cccccc"
            }
        };
    });

    // ✅ Layout de la figure
    const layout_wta = {
        title: "Evolution of ELO Ratings of the Top 10 WTA Players (2000–Present)",
        xaxis: {
            title: "Date",
            showgrid: false,
            showline: true,
            linecolor: "#0033a0",
            tickcolor: "#0033a0",
            color: "#0033a0"
        },
        yaxis: {
            title: "ELO",
            showgrid: false,
            showline: true,
            linecolor: "#0033a0",
            tickcolor: "#0033a0",
            color: "#0033a0"
        },
        paper_bgcolor: "#fff7f2",
        plot_bgcolor: "#fff7f2",
        font: {
            color: "#333",
            family: "sans-serif"
        },
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
            itemsizing: 'constant',
            tracegroupgap: 5
        },
        updatemenus: [{
            type: "buttons",
            showactive: false,
            direction: "down",
            x: -0.1,
            y: 1,
            buttons: [
                {
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
                }
            ],
            font: { color: "#0033a0" },
            bgcolor: "#fff7f2",
            bordercolor: "#fff7f2"
        }]
    };

    // ✅ Créer la figure animée
    Plotly.newPlot("graph-wta", initial_data_wta, layout_wta, {responsive: true}).then(() => {
        Plotly.addFrames("graph-wta", frames);
    });
});
