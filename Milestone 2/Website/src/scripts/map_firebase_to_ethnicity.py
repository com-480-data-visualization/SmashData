# %%
import pandas as pd
mappings = pd.read_csv("mapping.txt", header=None, dtype=(str, str))
mappings.columns = ["freebase", "wikidata"]
print(mappings.head())
print(mappings.dtypes)

wiki2freebase = mappings.set_index("wikidata")['freebase'].to_dict()



#%%

from pathlib import Path


files = list(Path(".").glob("Q*"))

print(files)

freebase_ids = []
wiki_ethnicities = []

for fi in files:
    with open(fi, "r") as f:
        file_content = f.read()
        ethnicity = "<unknown>"
        try:
            ethnicity = file_content.split("wikibase-title-label\">")[1].split("</span>")[0]
        except Exception:
            pass
        freebase_id = wiki2freebase[fi.stem]
        freebase_ids.append(freebase_id)
        wiki_ethnicities.append(ethnicity)
        print(f"{freebase_id} = {ethnicity}")


# %%

pd.DataFrame({"freebase_id": freebase_ids, "ethnicity": wiki_ethnicities}).to_csv("ethnicity_mappings.csv", sep=",", index=False)

# %%
