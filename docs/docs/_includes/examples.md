

# (to remove) Example components

- pour réajouter une "IMPACT IMAGE" (toute la largeur, ici c'est la banner mais il suffit de changer src)
<div class="big-image-wrapper">
  <img src="{{ '/assets/img/banner.jpg' | relative_url }}" alt="Alternative text" class="big-image">
</div>
<div class="big-image-spacer"></div>


- pour ajouter un tableau :

<table class="table table-striped">
  <thead>
    <tr>
      <th scope="col">#</th>
      <th scope="col">First</th>
      <th scope="col">Last</th>
      <th scope="col">Handle</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">1</th>
      <td>Mark</td>
      <td>Otto</td>
      <td>@mdo</td>
    </tr>
    <tr>
      <th scope="row">2</th>
      <td>Jacob</td>
      <td>Thornton</td>
      <td>@fat</td>
    </tr>
    <tr>
      <th scope="row">3</th>
      <td colspan="2">Larry the Bird</td>
      <td>@twitter</td>
    </tr>
  </tbody>
</table>

- pour ajouter un carousel

<div class="container-fluid">
  <div class="row justify-content-center">
    <div class="col-8">
      <p>Some text here</p>
    </div>
    <div class="col-4">
      {% include carousel.html %}
    </div>
  </div>
</div>

- pour ajouter un plot avec Plotly :

<!-- ATTENTION il faut que 'basic-plot' corresponde à l'argument de newPlot() dans basic_plot.js !! -->
<div id="basic-plot" style="width: 620px; height: 420px;"></div>
<script src="{{ '/assets/js/basic_plot.js' | relative_url }}"></script>

- pour ajouter des tabs simples :

<ul class="nav nav-underline" id="sampleTabs" role="tablist">
  <li class="nav-item" role="presentation">
    <button class="nav-link active" id="europe-wordcloud-tab" data-bs-toggle="tab" data-bs-target="#europe-wordcloud" type="button" role="tab" aria-controls="europe-wordcloud" aria-selected="true">
      Europe
    </button>
  </li>
  <li class="nav-item" role="presentation">
    <button class="nav-link" id="america-wordcloud-tab" data-bs-toggle="tab" data-bs-target="#america-wordcloud" type="button" role="tab" aria-controls="america-wordcloud" aria-selected="false">
      North America
    </button>
  </li>
</ul>

<div class="tab-content mt-3" id="sampleTabsContent">
  <div class="tab-pane fade show active" id="europe-wordcloud" role="tabpanel" aria-labelledby="europe-wordcloud-tab">
    <div class="card w-25">
      <img src="{{ '/assets/img/test1.jpg' | relative_url }}" alt="Image 1" class="card-img-top">
      <div class="card-body">
        <h4 class="card-title">Some more text here </h4>
        <p class="card-text">Description</p>
      </div>
    </div>
  </div>
  <div class="tab-pane fade" id="america-wordcloud" role="tabpanel" aria-labelledby="america-wordcloud-tab">
    <div class="card w-25">
    <img src="{{ '/assets/img/test2.jpg' | relative_url }}" alt="Image 2" class="card-img-top">
      <div class="card-body">
        <h4 class="card-title">Some more text here </h4>
        <p class="card-text">Description</p>
      </div>
    </div>
  </div>
</div>






<div style="text-align: center; position: relative; left: 15%; transform: scale(0.6);">
  <img src="/assets/img/Bouche_fermée.png" alt="Bouche fermée" style="position: absolute; top: -40%; left: -20%; width: 700%; height: 200%; z-index: 1; transition: opacity 0.3s ease-in-out;" onmouseover="this.style.display='none';">
  <img src="/assets/img/Bouche_ouverte.png" alt="Bouche ouverte" style="position: absolute; top: -40%; left: -20%; width: 700%; height: 170%; z-index: -1 ; opacity: 0; transition: opacity 0.3s ease-in-out;" onmouseover="this.style.opacity=1;">
  <!-- 1. Load the html template -->
  {% include movies_genres.html %}
  <!-- 2. Load the associated javascript -->
  <script src="{{ '/assets/js/movies_genres.js' | relative_url }}"></script>
</div>
