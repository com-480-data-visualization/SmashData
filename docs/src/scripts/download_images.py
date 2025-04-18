# Simple script to select a subset of movie posters in our subsets for milestone 3, and download them in the right directory

# %%
import pandas as pd
import requests


from pathlib import Path


data_p3 = Path("../../data/data_p3")
imgs_outdir = Path("../../docs/assets/img/movies")

files = list(data_p3.glob("*.csv"))

# %%

N_MOVIES = 5

subsets = {}
for f in files:
    curr_ds = pd.read_csv(f)
    curr_ds.dropna(axis=0, subset=["Poster", "imdbRating"], inplace=True)
    posters_urls = curr_ds.sort_values(by="imdbRating", ascending=False)["Poster"].head(20).sample(N_MOVIES).values.tolist()
    subsets[f.stem] = posters_urls

# %%
f2 = open("../../docs/_includes/carousel.html", "w+")
f2.write(r"""<div id="movieCarousel" class="carousel slide bg-body-secondary border rounded" data-bs-ride="carousel">
    <div class="carousel-inner">
        """)


subset_index = 0
first = True
for subset, urls in subsets.items():  
    movie_index = 0
    for url in urls:
        resp = requests.get(url)
        outfile = imgs_outdir / f"{subset_index}__{movie_index}.jpg"
        # with open(outfile, "wb") as f:
        #     f.write(resp.content)
        #     pass
        f2.write(r"""<div class="carousel-item{active} movie-poster">
            <img src="{start} '{local_url}' | relative_url {stop}" class="d-block h-100 ms-auto me-auto" alt="Movie Poster">
        </div>
        """.format(start='{{', stop='}}', active= ' active' if first else '', local_url=f"/assets/img/movies/{outfile.stem}.jpg"))
        first = False
        movie_index += 1
    subset_index += 1

f2.write(r"""    </div>
    <button class="carousel-control-prev" type="button" data-bs-target="#movieCarousel" data-bs-slide="prev">
        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Previous</span>
    </button>
    <button class="carousel-control-next" type="button" data-bs-target="#movieCarousel" data-bs-slide="next">
        <span class="carousel-control-next-icon" aria-hidden="true"></span>
        <span class="visually-hidden">Next</span>
    </button>
</div>""")
f2.close()

# %%
