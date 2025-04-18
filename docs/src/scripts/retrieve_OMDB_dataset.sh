#!/usr/bin/env bash

# =============================================================================================
# This script takes as input a txt file with one movie title per line, and retrieves the
# corresponding movie in the OMDB api (www.omdbapi.com)
#
# Usage  : ./retrieve_OMDB_dataset.sh <id>  # specify an ID to parallelize the process
# 
# For example, generate 4 splits of movie titles :
#  movies_titles_{0..3}.txt
#
# And run :
# $ ./retrieve_OMDB_dataset 0 &
# $ ./retrieve_OMDB_dataset 1 &
# $ ./retrieve_OMDB_dataset 2 &
# $ ./retrieve_OMDB_dataset 3 &
#
#
# This will output :
#  movies_omdbapi_{0..3}.json  # 4 files that you can merge manually or with any basic python
# =============================================================================================


export OMDBAPI=""

[[ -z "$OMDBAPI" ]] && echo "Specify an API key for OMDB at the top of the file !" && exit 1

ID=$1

[[ -z "$ID" ]] && echo "Usage : ./retrieve_OMDB_dataset.sh <id>" && exit 1

echo "ID=$ID"


# This contains only the titles
# generated with "cat movie.metadata.tsv | cut -d '	' -f3 > $MOVIE_TITLES_FILE"
MOVIE_TITLES_FILE="movies_titles_1_$ID.txt"

OUTPUT_FILE="movies_omdbapi_$ID.json"
ERRORS_FILE="omdbapi_errors_$ID.txt"
touch $ERRORS_FILE

COMMON_FILE="processed_titles"

# we check that the source file exists
[[ ! -f "$MOVIE_TITLES_FILE" ]] && echo "Input File '$MOVIE_TITLES_FILE' not found ! Please update MOVIE_TITLES_FILE variable. Exiting." && exit 1

# for each movie title we retrieve the corresponding omdb entry in a temporary file
TEMPORARY_FILE="tmp_$ID.json"

# This is to avoid repeating requests of the same movie
[[ "$ID" == "0" && -f $OUTPUT_FILE ]] && cat $OUTPUT_FILE | jq '.[].Title' >> "$COMMON_FILE"

while read -r MOVIE_TITLE ; do  # iterate on the lines of the input file

	# skip if the movie is already retrieved
	if grep -Fxq "\"$MOVIE_TITLE\"" "$COMMON_FILE"; then
		echo "$MOVIE_TITLE skipped - already retrieved"
		continue
	# skip if the movie is already errored
	elif grep -Fxq "$MOVIE_TITLE" $ERRORS_FILE; then
		echo "$MOVIE_TITLE skipped - already errored"  # check if in errors
		continue
	fi

	# replace spaces in the title with %20 to generate a valid URL
	TITLE_FORMATTED=$(echo $MOVIE_TITLE | sed -e "s/\s/\%20/g")

	# make the actual request and save it in TEMPORARY_FILE
	curl -s "http://www.omdbapi.com/?apikey=$OMDBAPI&t=$TITLE_FORMATTED" -o $TEMPORARY_FILE


	printf "\n\n---------------------------------------------\n"
	# Create the final output file if it does not exist
	if [[ ! -f $OUTPUT_FILE ]]; then
		echo "[$(cat $TEMPORARY_FILE)]" > $OUTPUT_FILE
		echo "Created $OUTPUT_FILE"

	# Else we append the result to the output file or the error file if the response is an error
	else
		if [[ "$(cat $TEMPORARY_FILE | jq -e '.Response')" == '"False"' ]]; then
			echo "Movie $MOVIE_TITLE was not found in OMDB, skipping it."
			echo "$MOVIE_TITLE $(cat $TEMPORARY_FILE)" >> $ERRORS_FILE
		else
			# append new result stored inside TEMPORARY_FILE to OUTPUT_FILE
			sed -i -e "s/\}\]$/\},/g" $OUTPUT_FILE
			cat $TEMPORARY_FILE >> $OUTPUT_FILE
			echo "]" >> $OUTPUT_FILE
		fi
	fi

	# pretty print the result
	echo "[ID=$ID]> '$MOVIE_TITLE' : $(cat $TEMPORARY_FILE)"

	# cooldown for when the API was limited (not limited anymore with the new API key)
    # if grep -Fq "Request limit reached" $TEMPORARY_FILE ; then
    #     echo "Limit reached, cooldown for 60s"
    #     sleep 60
    # fi
done < $MOVIE_TITLES_FILE


echo "DONE !"
echo "------------------------------------------------------------------------------"
echo "$(cat $OUTPUT_FILE | wc -l)/$(cat $MOVIE_TITLES_FILE | wc -l) movies found in OMDB API ($(cat $ERRORS_FILE | wc -l) errors stored in $ERRORS_FILE)"
echo "------------------------------------------------------------------------------"
