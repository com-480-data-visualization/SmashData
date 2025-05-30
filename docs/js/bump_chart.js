d3.json("assets/data/df_plotly.json").then(function(data) {
    // ✅ Nettoyage & prétraitement
    data.forEach(d => {
        d.date = new Date(d.Date);      // uniformiser
        d.rank = +d.Rank;
        d.player = d.Joueur;
    });

    // Teste si Rank est bien numérique
console.log("Sample:", data.slice(0, 5));
console.log("Bad values:", data.filter(d => isNaN(d.rank) || !d.date || !d.player));

    // ✅ Dates uniques triées
    const dates = Array.from(new Set(data.map(d => d.date))).sort((a, b) => a - b);

    // ✅ Top 10 joueurs les plus présents
    const topPlayers = Array.from(d3.group(data, d => d.player).entries())
        .sort((a, b) => b[1].length - a[1].length)
        .slice(0, 10)
        .map(d => d[0]);

    const width = 1000;
    const height = 600;
    const margin = { top: 40, right: 120, bottom: 60, left: 60 };

    const svg = d3.select("#graph").append("svg")
        .attr("width", width)
        .attr("height", height);

    const x = d3.scaleTime()
        .domain(d3.extent(dates))
        .range([margin.left, width - margin.right]);

    const y = d3.scaleLinear()
        .domain([1, 100]) // Rang 1 en haut
        .range([margin.top, height - margin.bottom]);

    const color = d3.scaleOrdinal(d3.schemeTableau10).domain(topPlayers);

    const lineGen = d3.line()
        .curve(d3.curveCatmullRom)
        .x(d => x(d.date))
        .y(d => y(d.rank));

    // Groupes de données par joueur
    const playerData = topPlayers.map(player => {
        return {
            player,
            values: dates.map(date => {
                const entry = data.find(d => d.player === player && +d.date === +date);
                return { date, rank: entry ? entry.rank : 100 }; // max rank if absent
            })
        };
    });

    // Ajouter une path vide pour chaque joueur
    const paths = svg.selectAll(".line")
        .data(playerData)
        .enter()
        .append("path")
        .attr("class", "line")
        .attr("stroke", d => color(d.player))
        .attr("stroke-width", 3)
        .attr("fill", "none");

    const dateLabel = svg.append("text")
        .attr("x", width - 150)
        .attr("y", margin.top)
        .attr("font-size", "20px")
        .attr("fill", "#333");

    // Animation
    let currentFrame = 1;
    let playing = false;
    let timer;

    function drawFrame(frame) {
        paths.attr("d", d => lineGen(d.values.slice(0, frame + 1)));
        dateLabel.text(dates[frame].toISOString().split("T")[0]);
    }

    function play() {
        if (playing) return;
        playing = true;
        timer = d3.interval(() => {
            drawFrame(currentFrame);
            currentFrame++;
            if (currentFrame >= dates.length) pause();
        }, 200);
    }

    function pause() {
        playing = false;
        if (timer) timer.stop();
    }

    function restart() {
        pause();
        currentFrame = 1;
        paths.attr("d", d => lineGen(d.values.slice(0, 1)));
        play();
    }

    // Boutons
    d3.select("#playBtn").on("click", play);
    d3.select("#pauseBtn").on("click", pause);
    d3.select("#restartBtn").on("click", restart);

    // Axes
    svg.append("g")
        .attr("transform", `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x));

    svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(y).ticks(10).tickFormat(d3.format("d")));

    // Init frame
    drawFrame(1);
});
