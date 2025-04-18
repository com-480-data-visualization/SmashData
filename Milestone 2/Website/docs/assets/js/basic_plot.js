var data = [{
    x: [1, 2, 3, 4, 5],
    y: [2, 3, 4, 5, 10],
    mode: 'lines+markers',
    type: 'scatter'
}];

var layout = {
    title: 'A Simple Plotly Chart',
    xaxis: { title: 'X-axis Label' },
    yaxis: { title: 'Y-axis Label' }
};

// ATTENTION il faut que 'basic-plot' corresponde à l'id de la div dans index.markdown !!
Plotly.newPlot('basic-plot', data, layout);
