// width and height
var margin = {top: 20, right: 60, bottom: 20, left: 40},
    width = 1200 - margin.left - margin.right,
    height = 650 - margin.top - margin.bottom;




var duration = 1000;

// main content holder
var svg = d3.select("#graph")
    .append("svg")
    .style("background", "#fff")
    .style("color", "#fff")
    .attr("width", width + margin.left + margin.right )
    .attr("height", height + margin.top + margin.bottom + 100 )
    .attr("class","graph-svg-component")
    .attr("fill", "currentColor")
    .attr("class","shadow")
    .attr("font-family", "sans-serif")
    .attr("font-size", 10)
    .append("g")
    .attr("transform","translate(" + (margin.left + 50)+ "," + (margin.top + 40) + ")"); 
   

// background grey    
svg.append("rect")
      .attr("x",0)
      .attr("y",35)
      .attr("height", height-30)
      .attr("width", width-100)
      .style("fill","#e5e5e5")
      //.style("fill", "url(#linear-gradient)")
      //.style("stroke", "black")
      .style("opacity", 0.01)  


// clip paths
svg.append("defs")
    .append("clipPath")
    .attr("id", "clip")
    .append("rect")
    .attr("x",10)
    .attr("y",35)
    .attr("width", width)
    .attr("height", height-30);  

svg.append("defs")
    .append("clipPath")
    .attr("id", "yaxisclip")
    .append("rect")
    .attr("x",-90)
    .attr("y",30)
    .attr("width", width)
    .attr("height", height);  
    
svg.append("defs")
    .append("clipPath")
    .attr("id", "xaxisclip")
    .append("rect")
    .attr("x",0)
    .attr("y",-(height-30))
    .attr("width", width-90)
    .attr("height", height+100);     

// title of the chart    
svg.append("text")
    .attr("class","title")
    .attr("x", (margin.left + width - margin.right) / 2)
    .attr("y", margin.top - 40)
    .attr("dy", 10)
    .attr("text-anchor", "middle")
    .style("fill","black")
    .text("Évolution des scores ELO des joueurs de tennis");

      
        
// time format    
var format = d3.timeFormat("%d-%b-%Y");
var parseTime = d3.timeParse("%Y-%m-%d");
var monthFormat = d3.timeFormat("%B %Y")

var color = d3.scaleOrdinal(d3.schemeTableau10)

// import json data
d3.json("src/data/elo_data.json").then(function(data){

   // create array of dict for colors and and icons 
   var case_types = [
  {"id":"Federer","title":"Roger Federer","color":["#D4AF37","#FFD700","#C5B358"],"flag":"/docs/assets/Roger Federer.png"},
  {"id":"Nadal","title":"Rafael Nadal","color":["#FF7F50","#FF4500","#DC143C"],"flag":"/docs/assets/Rafael Nadal.png"},
  {"id":"Djokovic","title":"Novak Djokovic","color":["#7FFFD4","#1E90FF","#00008B"],"flag":"/docs/assets/Roger Federer.png"}
];
    
    
    //create chunk
    Object.defineProperty(Array.prototype, 'chunk', {
        value: function(chunkSize) {
            var R = [];
            for (var i = 0; i < this.length; i += 1)
                R.push(this.slice(i, i + chunkSize));
            return R;
        }
    }); 


   var joueurs = Array.from(new Set(data.map(d => d.Joueur)));
   color.domain(joueurs);

    console.log("col name:",names);   

    // create chunked data

   
    // format dataset to be input in the line creation function
    // parser les dates et les ELO
    data.forEach(d => {
        d.Date = parseTime(d.Date);
        d.ELO = +d.ELO;
    });
    
    // regrouper les données par joueur
    var nested = d3.group(data, d => d.Joueur);
    
    // transformer pour correspondre à la structure D3
    var final = Array.from(nested, ([key, values]) => {
        return {
            name: key,
            value: values
                .sort((a, b) => d3.ascending(a.Date, b.Date))
                .map(d => ({
                    date: d.Date,
                    cases: d.ELO
                }))
        };
    });

    console.log("after formating data for input : ",final);


    // create color gradients
    for (let i in joueurs) {
    let joueur = joueurs[i];
    let joueurInfo = case_types.find(e => e.id === joueur);

    if (!joueurInfo) continue; // si pas trouvé, on skip

    var linearGradient = svg.append("defs")
        .append("linearGradient")
        .attr("gradientUnits", "userSpaceOnUse")
        .attr("id", "linear-gradient-" + joueurInfo.id);

    linearGradient.append("stop")
        .attr("offset", "5%")
        .attr("stop-color", joueurInfo.color[0]);

    linearGradient.append("stop")
        .attr("offset", "15%")
        .attr("stop-color", joueurInfo.color[1]);

    linearGradient.append("stop")
        .attr("offset", "35%")
        .attr("stop-color", joueurInfo.color[2]);
    }



    // initialize the line :
    line = d3.line()
        .curve(d3.curveBasis)
        .x(function(d){
            //console.log("line x:",x(new Date(d.date))); 
            return x(d.date);
        })
        .y(function(d){
            //console.log("line y:",y(d.cases));
            if (d.cases > 0){
                return y(d.cases);
            }else{
                return y(-2)
            }
            
    });

   // Initialise a X axis:
    x = d3.scaleTime()
        .range([0, width - 100])
    var xAxis = d3.axisBottom()
    .scale(x)
    .ticks(d3.timeWeek.every(1))
    .tickFormat(d3.timeFormat("%d-%b-%Y"))
    .tickSizeInner(-height)
    .tickPadding(10);


    svg.append("g")
        .attr("transform", `translate(10,${height})`)
        .attr("class","x axis")
        .attr("clip-path", "url(#xaxisclip)")
        .call(xAxis);   

    // Initialize an Y axis
    y = d3.scaleLinear().domain([0,1])
            .range([height , 2 * margin.top]);
    var yAxis = d3.axisLeft()
                .scale(y)
                .ticks(8)
                //.tickSizeInner(-(width-100));
    svg.append("g")
        .attr("transform", `translate(10,0)`)
        .attr("class","y axis") 
        .attr("clip-path", "url(#yaxisclip)")           


    var t = final[0].value;

    var month = monthFormat(t[t.length-1].date)
    var weekOfMonth = (0 | t[t.length-1].date.getDate() / 7)+1;


    let monthTxt =  svg.append("text")
        .attr("x",  (width)/2-50)
        .attr("y", height+50)
        .attr("dy", 10)
        .attr("text-anchor", "middle")
        .style("fill","black")
        .attr("font-weight", "bold")
        .attr("fill-opacity",0.0)
        .attr("font-size","16px")
        .text("← \xa0 "+month+" \xa0 →" );
        

    var intervalId = null;

    
    console.log("final after remove last data:",final);

    var index = 0;   
    //update[index];
 

    // update axis through out the loop in interval
    function updateAxis(){
        //update x axis
        svg.selectAll(".x.axis")
        .transition()
            .ease(d3.easeLinear)
            .duration(duration)
            .call(xAxis);


        // update y axis
        svg.selectAll(".y.axis")
            .transition()
            .ease(d3.easeCubic)
            .duration(1000)
            .call(yAxis);
    }

    // update line through out the loop in interval
    function makeLine(data){

        // generate line paths
        var lines = svg.selectAll(".line").data(data).attr("class","line");
            
        // transition from previous paths to new paths
        lines
        .transition()
        .ease(d3.easeLinear)
        .duration(duration)
        .attr("stroke-width", 5.0)
        //.attr("stroke-opacity", 1)
        .attr("stroke-opacity", function(d){
            if(d.value[d.value.length-1].cases>0){
                return 1;
            }else{
                return 0;
            }
        })
        .attr("d",d=> line(d.value))
        // .style("stroke", (d,i) =>
        //     color(d.name)
        // );
        .attr("stroke", (d,i) =>  "url(#linear-gradient-"+d.name+")" );
        //.attr("stroke", (d,i) =>  color(d.name) );

        // enter any new data
        lines
        .enter()
        .append("path")
        .attr("class","line")
        .attr("fill","none")
        .attr("stroke-linejoin", "round")
        .attr("stroke-linecap", "round")
        .attr("clip-path", "url(#clip)")
        .attr("stroke-width", 5.0)
        //.attr("stroke-opacity", 1)
        .attr("stroke-opacity", function(d){
            if(d.value[d.value.length-1].cases>0){
                return 1;
            }else{
                return 0;
            }
        })
        .transition()
        .ease(d3.easeLinear)
        .duration(duration)
        .attr("d",d=> line(d.value))
        // .style("stroke", (d,i) =>
        //     color(d.name)
        // )
        .attr("stroke", (d,i) =>  "url(#linear-gradient-"+d.name+")" );
        //.attr("stroke", (d,i) =>  color(d.name));

        // exit
        lines
        .exit()
        .transition()
        .ease(d3.easeLinear)
        .duration(duration)
        .remove();
    }
    
    // update tip circle through out the loop in interval
    function makeTipCircle(data){
        // add circle. generetare new circles
        circles = svg.selectAll(".circle").data(data)
                
        //transition from previous circles to new
        circles
        .enter()
        .append("circle")
        .attr("class","circle")
        .attr("fill", "white")
        .attr("clip-path", "url(#clip)")
        .attr("stroke", "black")
        .attr("stroke-width", 7.0)
        .attr("opacity",function(d){
            if(d.value[d.value.length-1].cases>0){
                return 1;
            }else{
                return 0;
            }
        })
        .attr("stroke-opacity", function(d,i){
            if(d.value[d.value.length-1].cases>0){
                return 1;
            }else{
                return 0;
            }
        })
        .attr("cx", d=> x(d.value[d.value.length-1].date))
        .attr("cy",function(d){

            if (d.value[d.value.length-1].cases > 0){
                return y(d.value[d.value.length-1].cases); 
            }else{
                return y(-2)
            } 
        })
        .attr("r",17)
        .transition()
        .ease(d3.easeLinear)
        .duration(duration)



        //enter new circles
        circles
        .transition()
        .ease(d3.easeLinear)
        .duration(duration)
        .attr("cx", d=> x(d.value[d.value.length-1].date))
        .attr("cy",function(d){
            if (d.value[d.value.length-1].cases > 0){
                return y(d.value[d.value.length-1].cases); 
            }else{
                return y(-2)
            } 
        })
        .attr("r",17)
        .attr("fill", "white")
        .attr("stroke", "black")
        .attr("stroke-width", 7.0)
        .attr("opacity",function(d){
            if(d.value[d.value.length-1].cases>0){
                return 1;
            }else{
                return 0;
            }
        })
        .attr("stroke-opacity", function(d,i){
            if(d.value[d.value.length-1].cases>0){
                return 1;
            }else{
                return 0;
            }
        })


        //remove and exit
        circles
        .exit()
        .transition()
        .ease(d3.easeLinear)
        .duration(duration)
        .attr("cx", d=> x(d.value[d.value.length-1].date))
        .attr("cy",function(d){  
            if (d.value[d.value.length-1].cases > 0){
                return y(d.value[d.value.length-1].cases); 
            }else{
                return y(-2)
            } 
        })
        .attr("r",17)
        .remove()
    }
    
    // update lables through out the loop in interval
    function makeLabels(data){
         //generate name labels
         names = svg.selectAll(".lineLable").data(data);
    
         //transition from previous name labels to new name labels
         names
         .enter()
         .append("text")
         .attr("class","lineLable")
         .attr("font-size","21px")
         .attr("clip-path", "url(#clip)")
         .style("fill",(d,i)=>case_types.find(e=>e.id === d.name).color[2])
         .attr("opacity",function(d){
            if(d.value[d.value.length-1].cases>0){
                return 1;
            }else{
                return 0;
            }
         })
         .transition()
         .ease(d3.easeLinear)
         .attr("x",function(d)
         {   
             return x(d.value[d.value.length-1].date)+30;
         })
         .style('text-anchor', 'start')
         .text(d => case_types.find(e=>e.id === d.name).title)
         .attr("y",function(d){  

            if (d.value[d.value.length-1].cases > 0){
                return y(d.value[d.value.length-1].cases) - 5;
            }else{
                return y(-2)
            }
         })
         
 
         // add new name labels
         names
         .transition()
         .ease(d3.easeLinear)
         .duration(duration)
         .attr("x",function(d)
         {   
             return x(d.value[d.value.length-1].date)+30;
         })
         .attr("y",function(d){
             
            if (d.value[d.value.length-1].cases > 0){
                return y(d.value[d.value.length-1].cases) - 5;
            }else{
                return y(-2)
            }
             
         })
         .attr("opacity",function(d){
            if(d.value[d.value.length-1].cases>0){
                return 1;
            }else{
                return 0;
            }
         })
         .attr("font-size","21px")
         .style("fill",(d,i)=>case_types.find(e=>e.id === d.name).color[2])
         .style('text-anchor', 'start')
         .text(d => case_types.find(e=>e.id === d.name).title)
 
         
         // exit name labels
         names.exit()
         .transition()
         .ease(d3.easeLinear)
         .duration(duration)
         .style('text-anchor', 'start')
         .remove();
 
 
 
         //generate labels
         labels = svg.selectAll(".label").data(data);
 
         //transition from previous labels to new labels
         labels
         .enter()
         .append("text")
         .attr("class","label")
         .attr("font-size","18px")
         .attr("clip-path", "url(#clip)")
         .style("fill",(d,i)=>case_types.find(e=>e.id === d.name).color[2])
         .attr("opacity",function(d){
            if(d.value[d.value.length-1].cases>0){
                return 1;
            }else{
                return 0;
            }
         })
         .transition()
         .ease(d3.easeLinear)
         .attr("x",function(d)
         {   
             return x(d.value[d.value.length-1].date)+30;
         })
         .style('text-anchor', 'start')
         .text(d => d3.format(',.0f')(d.value[d.value.length-1].cases))
         .attr("y",function(d){

            if (d.value[d.value.length-1].cases > 0){
                return y(d.value[d.value.length-1].cases)+15;
            }else{
                return y(-2)
            }             
         })
         
 
         // add new labels
         labels
         .transition()
         .ease(d3.easeLinear)
         .duration(duration)
         .attr("x",function(d)
         {   
             return x(d.value[d.value.length-1].date)+30;
         })
         .attr("y",function(d){
            
            if (d.value[d.value.length-1].cases > 0){
                return y(d.value[d.value.length-1].cases)+15;
            }else{
                return y(-2)
            } 

         })
         .attr("opacity",function(d){
            if(d.value[d.value.length-1].cases>0){
                return 1;
            }else{
                return 0;
            }
         })
         .attr("font-size","18px")
         .style("fill",(d,i)=>case_types.find(e=>e.id === d.name).color[2])
         .style('text-anchor', 'start')
         //.text(d => d3.format(',.0f')(d.value[d.value.length-1].cases))
         .tween("text", function(d) {
          if (d.value.length >= 2 && d.value[d.value.length - 1].cases !== 0) {
              let i = d3.interpolateRound(d.value[d.value.length - 2].cases, d.value[d.value.length - 1].cases);
              return function(t) {
                  this.textContent = d3.format(',')(i(t));
              };
          } else if (d.value.length === 1) {
              this.textContent = d3.format(',')(d.value[0].cases);
          }
        });

 
         
         // exit labels
         labels.exit()
         .transition()
         .ease(d3.easeCubic)
         .duration(duration)
         .style('text-anchor', 'start')
         .remove();
         
    }

    // update icons through out the loop in interval
    function makeImages(data){
        //select all images
        images = svg.selectAll(".image").data(data)
            
        images
        .enter()
        .append("image")
        .attr("class","image")
        .attr("clip-path", "url(#clip)")
        .attr('xlink:href', d => case_types.find(e => e.id === d.name)?.flag || "")        .attr("width", 40)
        .attr("height", 40)
        .attr("opacity",function(d){
            if(d.value[d.value.length-1].cases>0){
                return 1;
            }else{
                return 0;
            }
        })
        .attr("y", function (d) {
            if (d.value[d.value.length-1].cases > 0){
                return y(d.value[d.value.length-1].cases)-20;
            }else{
                return y(-2)-15;
            }
             
        })
        .attr("x", function (d) { return x(d.value[d.value.length-1].date)-20; })
        .attr("preserveAspectRatio", "none")
        .transition()
        .ease(d3.easeLinear)
        .duration(duration);

         //enter new circles
         images
         .transition()
         .ease(d3.easeLinear)
         .duration(duration)
         .attr('xlink:href', d => case_types.find(e => e.id === d.name)?.flag || "")
         .attr("width", 40)
         .attr("height", 40)
         .attr("opacity",function(d){
            if(d.value[d.value.length-1].cases>0){
                return 1;
            }else{
                return 0;
            }
         })
         .attr("x", d=> x(d.value[d.value.length-1].date)-20)
         .attr("y", function (d) {
            if (d.value[d.value.length-1].cases > 0){
                return y(d.value[d.value.length-1].cases)-20;
            }else{
                return y(-2)-15;
            }
          })
         .attr("preserveAspectRatio", "none");

         //remove and exit
        images.exit()
        .transition()
        .ease(d3.easeLinear)
        .duration(duration)
   
        .remove()
    }

    var yaxismaxlimit = 0;
    
    // function to update the line in each frame
var index = 1;

function update() {
    if (index > dates.length) return;

    let currentDate = dates[index - 1];

    // Pour chaque joueur, ne garder que les points jusqu'à la date actuelle
    let currentData = final.map(player => {
        return {
            name: player.name,
            value: player.value.filter(d => d.date <= currentDate)
        };
    });

    // Mise à jour des domaines
    x.domain(d3.extent(dates.slice(0, index)));
    y.domain([
        0,
        d3.max(currentData, d => d3.max(d.value, v => v.cases)) || 1
    ]).nice();

    updateAxis();
    makeLine(currentData);
    makeTipCircle(currentData);
    makeImages(currentData);
    makeLabels(currentData);

    // Met à jour le texte du mois
    var month = monthFormat(currentDate);
    monthTxt
        .transition()
        .ease(d3.easeCubic)
        .duration(800)
        .attr("fill-opacity", 0.7)
        .text("← \xa0 " + month + " \xa0 →");

    index++;
    setTimeout(update, duration);
}


update();

});
