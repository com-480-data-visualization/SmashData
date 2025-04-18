"""Builds a file arborescence to be fed to the CoreNLP pipeline.

  - Traverse the dataframe and gather the ids of the movies that have not their plot processed by the pipeline
  - For each id, create a new file named <Wikipedia_ID>.txt containing the unprocessed plot (taken from OMDB).
  - Create a file containing all the paths to the previous files, one path per line.

  Inside IntelliJ, you can clone the stanford CoreNLP pipeline, install the dependencies, and add a new
  run configuration with the template given inside "INTELLIJ_run_Stanford_Pipeline.xml". Set the "-fileList"
  argument to point to the file created by this script ("corenlp_input.txt"). Click on RUN.

  This will create files of form <Wikipedia_ID>.txt.xml containing the output of the pipeline for this id.
"""

from pathlib import Path

import pandas as pd

DATASET_FILEPATH = Path("../../data/merged_movie_metadata.csv")
PROCESSED_PLOT_FOLDER = Path("../../../corenlp_plot_summaries")

assert DATASET_FILEPATH.exists(), "Must configure the correct path to merged_movie_metadata.tsv"
assert PROCESSED_PLOT_FOLDER.exists(), "Must configure the correct path to corenlp_plot_summaries"

df = pd.read_csv(DATASET_FILEPATH)



# Count matching folders/files
processed_ids = {f.stem.replace(".xml", "")
                 for f in PROCESSED_PLOT_FOLDER.glob("*.xml.gz")}
available_ids = set(df["Wikipedia_ID"].astype(str))
matching_files = [
    PROCESSED_PLOT_FOLDER/f"{filename}.xml.gz" for filename in processed_ids.intersection(available_ids)]

print(f"Number of matching folders/files: {len(matching_files)}")
print(f"Number of unique Wiki id's: {df['Wikipedia_ID'].nunique()}")

# Count unmatched folders/file
unprocessed_ids = available_ids.difference(processed_ids)
unprocessed_plots = df[df["Wikipedia_ID"].astype(str).isin(unprocessed_ids)][[
    "Wikipedia_ID", "Plot"]]
unprocessed_plots.dropna(subset="Plot", inplace=True)
print(unprocessed_plots)

print("Writing as a list of files to process")
for index, row in unprocessed_plots.iterrows():
    with open(f"../corenlp_plot_summaries/surprocess/{row['Wikipedia_ID']}.txt", "w+") as f:
        f.write(row['Plot'])

with open(f"corenlp_input.txt", "w+") as f:
    f.writelines([f"{str(Path(f'../corenlp_plot_summaries/surprocess/{unprocessed_id}.txt').resolve())}\n"
                    for unprocessed_id in unprocessed_plots['Wikipedia_ID'].tolist()])

print("Written : corenlp_input.txt")

print("""Inside IntelliJ, you can clone the stanford CoreNLP pipeline and install the dependencies, and add a new
run configuration with the template given inside "INTELLIJ_run_Stanford_Pipeline.xml". Set the "-fileList"
argument to point to the file created by this script ("corenlp_input.txt"). Click on RUN.

This will create files of form <Wikipedia_ID>.txt.xml containing the output of the pipeline for this id.""")

