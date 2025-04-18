#!/usr/bin/env bash

RDF_FILE="fb2w.nt"
IDS_FILE="ids.txt"

while read -r FIREBASE_ID ; do  # iterate on the lines of the input file
    printf "\n\n================================\n"
    WIKIPEDIA_ID=$(grep -e "m\.$FIREBASE_ID>" $RDF_FILE | cut -d '/' -f14 | cut -d '>' -f1)
    echo "$FIREBASE_ID -> "
    
    curl -s "https://www.wikidata.org/wiki/$WIKIPEDIA_ID" -O pages/$WIKIPEDIA_ID


done < $IDS_FILE


