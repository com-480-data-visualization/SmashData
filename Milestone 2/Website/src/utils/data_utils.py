# import
from collections import Counter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from tqdm import tqdm
from scipy import stats
from nltk import word_tokenize, ngrams
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import gzip
import xml.etree.ElementTree as ET
import re
import json
import ast

def determine_types(genres):
    """
    Determines the types of genres for a film using main keywords and substring searches.

    :param genres: list of str or str, the list of genres for a film (or a string representation)
    :return: list, a list of associated types for the film, without duplicates
    """
    # initialize a set to store unique types
    types = set()

    # convert the string to a list if necessary
    if isinstance(genres, str):
        try:
            genres = ast.literal_eval(genres)
        except (ValueError, SyntaxError):
            return ['Comedy_Other']  # return 'Comedy_Other' if conversion fails

    # check if genres is a list
    if not isinstance(genres, list):
        return ['Comedy_Other']

    # combine all genres into a single lowercase string
    genres_text = " ".join(genres).lower()

    # iterate through the genre keywords dictionary and add types based on matches
    for type_name, keywords in genre_keywords.items():
        if any(keyword.lower() in genres_text for keyword in keywords):
            types.add(type_name)  # add to the set to avoid duplicates

    # add 'Comedy_Other' if no specific type is found
    if not types:
        types.add('Comedy_Other')
    
    return list(types)


def simplify_continent(continent_list):
    """
    Simplifies the 'Continents' column to have only the values 'Europe', 'America', or 'Both'.

    :param continent_list: list of str, list of continents associated with a film
    :return: str, simplified continent value ('Europe', 'America', 'Both', or 'Other')
    """
    # check for films associated with both Europe and America
    if 'Europe' in continent_list and 'America' in continent_list or 'Both' in continent_list:
        return 'Both'
    # check for films associated only with Europe
    elif 'Europe' in continent_list:
        return 'Europe'
    # check for films associated only with America
    elif 'America' in continent_list:
        return 'America'
    # assign 'Other' for all other cases
    else:
        return 'Other'



def remove_outliers(data, column):
    """
    Filters out outliers from a dataset based on the interquartile range (IQR).

    :param data: pd.DataFrame, the input dataset
    :param column: str, the name of the column to check for outliers
    :return: pd.DataFrame, the dataset with outliers removed
    """
    # calculate the first and third quartiles
    Q1, Q3 = data[column].quantile([0.25, 0.75])
    
    # compute the interquartile range (IQR)
    IQR = Q3 - Q1
    
    # determine the lower and upper bounds for outlier detection
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # filter the data to exclude outliers
    return data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]


def get_sorted_coefficients(regressor, feature_names, region):
    """
    Retrieves and sorts the coefficients of a regressor by their absolute values.

    :param regressor: sklearn regressor, the trained regression model
    :param feature_names: list, names of the features corresponding to the coefficients
    :param region: str, name of the region for context in the output
    :return: pd.DataFrame, sorted DataFrame of features and their coefficients
    """
    # create a DataFrame with features and their coefficients
    coefficients = pd.DataFrame({
        'Feature': feature_names,
        'Coefficient': regressor.coef_
    })
    
    # add a column for the absolute values of the coefficients
    coefficients['Absolute_Coefficient'] = coefficients['Coefficient'].abs()
    
    # sort the DataFrame by absolute coefficient values in descending order
    coefficients = coefficients.sort_values(by='Absolute_Coefficient', ascending=False).drop(columns='Absolute_Coefficient')
    
    # print the top coefficients for the specified region
    print(f"Top coefficients for {region}:")
    display(coefficients)
    
    return coefficients


def get_word_count(tokenized_plots):
    """
    Returns a Counter of word occurrences in tokenized plots.

    :param tokenized_plots: pd.Series, tokenized plots
    :return: Counter, occurrences of words across all tokenized plots
    """
    # drop missing values and flatten the tokenized plots into a single list
    return Counter(tokenized_plots.dropna().explode())

# initialize the lemmatizer and define the set of English stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


def compare_ratings(user_ratings, critic_ratings, continent):
    """
    Compares user and critic ratings for films using statistical tests.

    Decides between a T-Test or Mann-Whitney U Test based on normality of the distributions.
    
    :param user_ratings: pd.Series or list, ratings provided by users
    :param critic_ratings: pd.Series or list, ratings provided by critics
    :param continent: str, the name of the continent for context in the output
    :return: None, prints the test results
    """
    # check normality of both distributions to determine the appropriate test
    if stats.shapiro(user_ratings).pvalue > 0.05 and stats.shapiro(critic_ratings).pvalue > 0.05:
        # if both distributions are normal, use an independent T-Test
        t_stat, p_value = stats.ttest_ind(user_ratings, critic_ratings, alternative='greater', equal_var=False)
        test_name = "T-Test"
    else:
        # use Mann-Whitney U Test if data is not normally distributed
        u_stat, p_value = stats.mannwhitneyu(user_ratings, critic_ratings, alternative='greater')
        test_name = "Mann-Whitney U Test"
    
    # output the results
    print(f"\n{test_name} Results for {continent} Films:")
    print(f"P-Value: {p_value}")
    if p_value < 0.05:
        print("Result: Critics rate films more severely than users (significant difference).")
    else:
        print("Result: No significant difference between critics' and users' ratings.")



def tok(sentence):
    """
    Tokenize and lemmatize a sentence, removing stop words.

    :param sentence: str, the sentence to tokenize
    :return: list, lemmatized tokens without stop words
    """
    # tokenize the sentence
    tokenized = word_tokenize(sentence)
    
    # lemmatize, convert to lowercase, and remove non-alphabetic words and stop words
    return [
        lemmatizer.lemmatize(word.lower()) 
        for word in tokenized 
        if word.isalpha() and word.lower() not in stop_words
    ]



def tok_by_region(df, region):
    """
    Tokenizes plot summaries for films in a specific region.

    :param df: pd.DataFrame, the dataset containing film data
    :param region: str, the name of the region to filter (e.g., 'America', 'Europe')
    :return: pd.Series, tokenized plot summaries for the specified region
    """
    return df[df['Continents'].str.contains(region)].apply(
        lambda row: tok(row['Plot_Summary_Base']) if pd.notna(row['Plot_Summary_Base'])
        else tok(row['Plot']) if pd.notna(row['Plot']) else np.nan,
        axis=1
    )


def filter_words_by_pos(tokens_metadata, pos_tags):
    """
    Filters words based on specified Part-of-Speech (POS) tags.

    :param tokens_metadata: list of dict, metadata for each word in a sentence, including 'word' and 'POS' keys
    :param pos_tags: list of str, POS tags to retain
    :return: list of str, words filtered by the specified POS tags
    """
    # filter and return words whose POS matches the specified tags
    return [entry['word'] for entry in tokens_metadata if entry['POS'] in pos_tags]




def filter_words_by_pos_ngram(tokens_metadata, pos_tags, ngram):
    """
    Filters and generates n-grams where the first token matches specified POS tags.

    :param tokens_metadata: list of dict, metadata for each word in a summary, including 'word' and 'POS' keys
    :param pos_tags: list of str, POS tags to filter the first token of the n-gram
    :param ngram: int, the length of the n-gram
    :return: list of str, n-grams where the first token matches one of the specified POS tags
    """
    results = []
    # iterate through n-grams generated from tokens_metadata
    for ngram_instance in ngrams(tokens_metadata, ngram):
        # check if the first token's POS is in the specified tags
        if ngram_instance[0]['POS'] in pos_tags:
            # join words in the n-gram and add to results
            results.append(' '.join(entry['word'] for entry in ngram_instance))
    return results

def get_sentence_word_metadata(folder_path, id, print_output=False):
    """
    Retrieves Stanford CoreNLP metadata for a given ID from .xml.gz files.

    :param folder_path: Path, the path to the folder containing the processed summaries
    :param id: str, Wikipedia ID of the movie used to locate the corresponding .xml.gz file
    :param print_output: bool, whether to print the metadata for each sentence
    :return: list of dict, metadata for each word in the summary
    """
    # construct the file path for the .xml.gz file
    gz_file_path = folder_path.resolve() / f"{id}.xml.gz"
    
    # check if the file exists
    if not gz_file_path.is_file():
        return []
    
    try:
        # open and read the compressed .xml.gz file
        with gzip.open(gz_file_path, 'rb') as gz_file:
            xml_data = gz_file.read()
            root = ET.fromstring(xml_data.decode())
        
        summary_word_metadata = []

        # iterate over sentences in the XML structure
        for sentence in root[0][0]:
            if print_output:
                print(f"\n\n=================== Sentence n°{sentence.attrib['id']} ===================")
            
            # iterate over the tokens in each sentence
            for child in sentence:
                if child.tag != "tokens":
                    continue
                for token in child:
                    attribs = {c.tag: c.text for c in token}
                    if print_output:
                        print(f"{attribs['word']} ({attribs['lemma']}) => {attribs['POS']}")
                    
                    # include only alphabetic words (exclude punctuation, etc.)
                    if attribs['word'].isalpha():
                        summary_word_metadata.append(attribs)
        
        return summary_word_metadata
    
    except Exception as e:
        print(f"Error processing {gz_file_path}: {e}")
        return []


def generate_word_cloud_on_subset(
    region, pos_tags, title, folder_path, region_ids, dataset_subsets,
    mask_image=None, sample_output=True, ngrams=1, subset_name=None, store_to=None, dpi=300
):
    """
    Generates a word cloud for a specified region, subset, and POS tags, with optional mask and sample output.

    :param region: str, the name of the region (e.g., 'America', 'Europe')
    :param pos_tags: list of str, POS tags to filter the words
    :param title: str, the title for the word cloud
    :param folder_path: Path, the folder containing processed summaries
    :param region_ids: dict, mapping regions to sets of Wikipedia IDs
    :param dataset_subsets: dict, subsets of the dataset to filter IDs
    :param mask_image: np.array or None, optional mask image for the word cloud shape
    :param sample_output: bool, whether to display a sample of the most common words
    :param ngrams: int, size of n-grams to generate (default: 1 for single words)
    :param subset_name: str or None, name of the subset to filter IDs (default: None)
    :param store_to: str or None, file path to save the word cloud (default: None to display)
    :param dpi: int, resolution for saving the word cloud (default: 300)
    :return: None
    """
    # filter the region IDs based on the subset name if provided
    subset_ids = set()
    if subset_name and subset_name in dataset_subsets:
        subset_ids = set(dataset_subsets[subset_name]['Wikipedia_ID'].astype(str))
    
    # intersect region IDs with subset IDs or use region IDs directly
    region_subset_ids = region_ids[region].intersection(subset_ids) if subset_name else region_ids[region]
    
    # initialize a counter for word frequencies
    word_counter = Counter()
    
    # process each Wikipedia ID in the filtered set
    for wiki_id in tqdm(region_subset_ids, desc=f"Processing {region} - {title}"):
        tokens_metadata = get_sentence_word_metadata(folder_path, wiki_id)
        # filter words by POS tags or generate n-grams
        if ngrams == 1:
            filtered_words = filter_words_by_pos(tokens_metadata, pos_tags)
        else:
            filtered_words = filter_words_by_pos_ngram(tokens_metadata, pos_tags, ngrams)
        # update the word counter with filtered words
        word_counter.update(filtered_words)
    
    # print a sample of the most common words for verification if enabled
    if sample_output:
        print(f"\nSample of filtered words for {region} - {title}:")
        print(word_counter.most_common(10))
    
    # generate the word cloud from the word frequencies
    wordcloud = WordCloud(
        width=800, height=400, background_color='white', mask=mask_image,
        contour_color='black', contour_width=1
    ).generate_from_frequencies(word_counter)
    
    # display or save the word cloud
    plt.figure(figsize=(10, 5), dpi=dpi)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title)
    if store_to:
        plt.savefig(store_to, dpi=dpi, bbox_inches='tight', pad_inches=0.1)
    else:
        plt.show()


continent_classification = {
    'America': [
        'United States of America', 'Canada', 'Mexico', 'Argentina', 'Brazil', 'Chile', 'Cuba', 'Colombia', 
        'Uruguay', 'Venezuela', 'Jamaica', 'Panama', 'Costa Rica', 'Bahamas', 'Haiti', 'Puerto Rico', 'Bolivia', 'Peru'
    ],
    'Europe': [
        'United Kingdom', 'France', 'Italy', 'Germany', 'West Germany', 'Soviet Union', 'Poland', 'Czechoslovakia', 
        'Belgium', 'Norway', 'Hungary', 'German Democratic Republic', 'Yugoslavia', 'Ireland', 'Switzerland', 'Austria', 
        'Finland', 'Czech Republic', 'Russia', 'Turkey', 'England', 'Greece', 'Portugal', 'Croatia', 'Romania', 
        'Iceland', 'Luxembourg', 'Weimar Republic', 'Serbia', 'Scotland', 'Estonia', 'Bosnia and Herzegovina', 'Slovakia', 
        'Slovenia', 'Albania', 'Ukraine', 'Azerbaijan', 'Nazi Germany', 'Republic of Macedonia', 'Socialist Federal Republic of Yugoslavia', 
        'Serbia and Montenegro', 'Georgia', 'Lithuania', 'Armenia', 'Kingdom of Great Britain', 'Federal Republic of Yugoslavia', 
        'Georgian SSR', 'Slovak Republic', 'Malta', 'Northern Ireland', 'Montenegro', 'Kingdom of Italy', 'Monaco', 'Cyprus', 
        'Ukrainian SSR', 'Isle of Man', 'Soviet occupation zone', 'German Language', 'Ukranian SSR', 'Spain', 'Netherlands', 
        'Sweden', 'Denmark', 'Bulgaria', 'Wales'
    ],
    'Asia': [
        'India', 'Japan', 'Hong Kong', 'China', 'Israel', 'Iran', 'Thailand', 'Pakistan', 'Taiwan', 'Indonesia', 'Malaysia', 
        'Sri Lanka', 'Singapore', 'Cambodia', 'Bangladesh', 'Nepal', 'Lebanon', 'Vietnam', 'Korea', 'Burma', 'Iraq', 
        'United Arab Emirates', 'Afghanistan', 'Iraqi Kurdistan', 'Uzbek SSR', 'Uzbekistan', 'Mongolia', 'Kuwait', 
        'Bhutan', 'Aruba', 'Bahrain', 'Qatar', 'Jordan', 'Turkmenistan', 'Republic of China', 'Macau', 
        'Palestinian Territories', 'Mandatory Palestine', 'Palestinian territories', 'Malayalam Language', 'South Korea', 'Philippines'
    ],
    'Africa': [
        'South Africa', 'Egypt', 'Morocco', 'Algeria', 'Tunisia', 'Burkina Faso', 'Senegal', 'Nigeria', 
        'Democratic Republic of the Congo', 'Mali', 'Kenya', 'Cameroon', 'Ethiopia', 'Zimbabwe', 'Guinea', 'Libya', 
        'Guinea-Bissau', 'Congo', 'Zambia'
    ],
    'Oceania': [
        'Australia', 'New Zealand'
    ]
}

def map_country_to_continent(country):
    """
    Maps a given country to its corresponding continent.

    :param country: str, the name of the country
    :return: str, the name of the continent or 'Other' if not found
    """
    for continent, countries in continent_classification.items():
        if country in countries:
            return continent
    return 'Other'


def map_country_list_to_continent(country_list):
    """
    Maps a list of countries to their corresponding continents.

    :param country_list: list of str, names of the countries
    :return: list of str, names of the corresponding continents
    """
    return [map_country_to_continent(country) for country in country_list]


def treat_continent(continent):
    """
    Processes a list of continents and determines the appropriate classification.

    :param continent: list of str, a list of continents associated with an entity
    :return: list of str, processed list of continents with combined classifications if applicable
    """
    new_continent = []

    # handle the case where both America and Europe are present
    if "America" in continent and "Europe" in continent:
        new_continent.append("Both")
    else:
        # add individual continents for America and Europe if present
        if "America" in continent:
            new_continent.append("America")
        if "Europe" in continent:
            new_continent.append("Europe")
    
    # check and add other continents if present
    if "Asia" in continent:
        new_continent.append("Asia")
    if "Africa" in continent:
        new_continent.append("Africa")
    if "Oceania" in continent:
        new_continent.append("Oceania")
    
    return new_continent



def extract_awards(awards_str):
    """
    Extracts the number of Oscars, nominations, and wins from the Awards column.

    :param awards_str: str, the string describing awards (e.g., "Won 2 Oscars, 5 wins & 8 nominations")
    :return: tuple (int, int, int), counts of Oscars, nominations, and wins
    """
    # handle cases where the awards string is missing
    if pd.isna(awards_str):
        return 0, 0, 0

    # initialize counts
    oscar = 0
    nomination = 0
    win = 0

    # extract the number of Oscars won
    oscar_match = re.search(r'Won (\d+) Oscar', awards_str)
    if oscar_match:
        oscar = int(oscar_match.group(1))

    # extract the number of nominations
    nomination_match = re.search(r'(\d+) nomination', awards_str)
    if nomination_match:
        nomination = int(nomination_match.group(1))

    # extract the number of other wins
    win_match = re.search(r'(\d+) win', awards_str)
    if win_match:
        win = int(win_match.group(1))

    # return the counts as a tuple
    return oscar, nomination, win



def extract_ratings(ratings_str):
    """
    Extracts ratings from the Ratings column and converts them into a dictionary.

    :param ratings_str: str, the string representation of ratings (e.g., JSON-like format)
    :return: dict, a dictionary with rating sources as keys and their values as values
    """
    # handle cases where the ratings string is missing or empty
    if pd.isna(ratings_str) or ratings_str == '[]':
        return {}

    # parse the JSON-like string and convert it to a dictionary
    ratings_list = json.loads(ratings_str.replace("'", '"'))
    ratings_dict = {rating['Source']: rating['Value'] for rating in ratings_list}

    return ratings_dict



def convert_to_scale_of_10(rating):
    """
    Converts a given rating to a scale of 10.

    :param rating: str or float, the rating value (e.g., "85%", "8.5/10", "85/100")
    :return: float or None, the rating converted to a scale of 10, or None if the input is invalid
    """
    # handle cases where the rating is missing
    if pd.isna(rating):
        return None

    # process string ratings
    if isinstance(rating, str):
        if '%' in rating:
            # convert percentage to a scale of 10
            return float(rating.replace('%', '')) / 10
        if '/10' in rating:
            # extract and return the numeric value
            return float(rating.replace('/10', ''))
        if '/100' in rating:
            # convert out-of-100 ratings to a scale of 10
            return float(rating.replace('/100', '')) / 10

    # return the rating as a float if it's already numeric
    return float(rating)



def classifier_age(rating):
    """
    Classifies age ratings into standardized categories.

    :param rating: str, the age rating of a movie or TV show
    :return: str, the standardized age classification
        - "All Audiences (TP)"
        - "Recommended Parental Agreement (AP)"
        - "13+"
        - "16+"
        - "18+"
        - "Not Rated"
    """
    # classify ratings for all audiences
    if rating in ["G", "TV-G", "U", "Approved", "EM"]:
        return "All Audiences (TP)"

    # classify ratings requiring parental agreement
    elif rating in ["PG", "PG-13", "TV-PG", "TV-Y7", "TV-Y7-FV", "Atp"]:
        return "Recommended Parental Agreement (AP)"

    # classify ratings for 13+ audiences
    elif rating in ["13+", "TV-14", "M/PG", "M"]:
        return "13+"

    # classify ratings for 16+ audiences
    elif rating in ["R", "TV-MA", "16+", "NC-17"]:
        return "16+"

    # classify ratings for 18+ audiences
    elif rating in ["X", "AO", "18"]:
        return "18+"

    # fallback for unrated or unrecognized ratings
    else:
        return "Not Rated"

    

# Dictionnaire pour les mots-clés principaux par type
genre_keywords = {
    'Comedy_Romance': ['romance', 'romantic'],
    'Comedy_Drama': ['drama', 'tragedy', 'tragicomedy', 'melodrama'],
    'Comedy_Action': ['action', 'action comedy', 'martial arts film', 'superhero'],
    'Comedy_Adventure': ['adventure', 'action/adventure', 'family-oriented adventure', 'road movie'],
    'Comedy_Horror': ['horror', 'slasher', 'sci-fi horror', 'natural horror', 'haunted house film', 'horror comedy'],
    'Comedy_Musical': ['musical', 'hip hop', 'dance', 'opera', 'jukebox musical'],
    'Comedy_Crime': ['crime', 'crime fiction', 'crime drama', 'heist', 'detective', 'gangster film'],
    'Comedy_Western': ['western', 'spaghetti western', 'comedy western', 'revisionist western'],
    'Comedy_Documentary': ['documentary', 'docudrama', 'mockumentary', 'rockumentary'],
    'Comedy_LGBT': ['lgbt', 'gay', 'gay interest', 'gay themed'],
    'Comedy_Fantasy': ['fantasy', 'fairy tale', 'fantasy adventure', 'supernatural'],
    'Comedy_Thriller': ['thriller', 'suspense', 'mystery', 'spy', 'political thriller', 'psychological thriller'],
    'Comedy_Animation': ['animation', 'computer animation', 'animated cartoon', 'anime', 'stop motion'],
    'Comedy_Parody': ['parody', 'comedy of errors', 'satire', 'media satire'],
    'Comedy_Satire': ['satire', 'political satire', 'absurdism'],
    'Comedy_Mockumentary': ['mockumentary', 'pseudo-documentary', 'satirical documentary'],
    'Comedy_Sports': ['sports', 'boxing', 'baseball', 'basketball', 'soccer'],
    'Comedy_Political': ['political', 'political drama', 'political cinema'],
    'Comedy_Adult': ['adult', 'erotic', 'sexploitation', 'pornography', 'softcore porn','sex comedy'],
    'Comedy_Blaxploitation': ['blaxploitation'],
    'Comedy_Science_Fiction': ['science', 'sci-fi', 'science fiction', 'time travel', 'superhero', 'dystopia'],
    'Comedy_Black': ['black comedy', 'dark humor', 'gallows humor'],
    'Comedy_Teen': ['teen', 'coming of age', 'teen drama', 'high school'],
    'Comedy_Family': ['family', 'children', 'family film', 'children’s/family','domestic comedy'],
    'Comedy_Slapstick': ['slapstick', 'physical comedy', 'gross-out', 'gross-out film'],
    'Comedy_Screwball': ['screwball', 'screwball comedy', 'comedy of manners'],
    'Comedy_Buddy': ['buddy film', 'buddy cop', 'buddy comedy'],
    'Comedy_Superhero': ['superhero', 'comic book', 'comic superheroes'],
    'Comedy_War': ['war film', 'anti-war', 'military comedy'],
    'Comedy_Road_movie': ['road movie', 'road comedy', 'road trip'],
    'Comedy_Holiday': ['holiday', 'christmas', 'christmas movie', 'holiday film'],

}


def plot_frequencie_proportion(data, title, xlabel, color="skyblue", figsize=(8, 6)):
    """
    Plots a bar chart for a distribution with proportion labels on top of the bars.

    :param data: pd.Series, a pandas Series containing the data to plot
    :param title: str, the title of the plot
    :param xlabel: str, the label for the x-axis
    :param color: str, the color of the bars (default: "skyblue")
    :param figsize: tuple, the size of the plot (default: (8, 6))
    :return: None
    """
    # calculate counts and proportions
    total_count = data.sum()
    proportions = (data / total_count).values  # proportions as percentages

    # create the figure and plot the bar chart
    plt.figure(figsize=figsize)
    ax = data.plot(kind="bar", color=color)
    ax.set_title(title, fontsize=16, fontweight="bold")
    ax.set_xlabel(xlabel, fontsize=14, fontweight="bold")
    ax.set_ylabel("Frequency", fontsize=14, fontweight="bold")
    ax.tick_params(axis='x', rotation=45)

    # add proportion labels to each bar
    for rect, label in zip(ax.patches, proportions):
        ax.text(
            rect.get_x() + rect.get_width() / 2,  # x position
            rect.get_height(),  # y position (top of the bar)
            f"{label:.2%}",  # format as a percentage
            ha="center",  # horizontally center-aligned
            va="bottom",  # vertically center-aligned
            fontsize=10  # font size for the label
        )

    # adjust layout and show the plot
    plt.tight_layout()
    plt.show()


def plot_frequencie(data, title, xlabel, color="skyblue", figsize=(8, 6)):
    """
    Plots a bar chart for a given data distribution with value labels.

    :param data: pd.Series, a pandas Series containing the data to plot
    :param title: str, the title of the plot
    :param xlabel: str, the label for the x-axis
    :param color: str, the color of the bars (default: "skyblue")
    :param figsize: tuple, the size of the plot (default: (8, 6))
    :return: None
    """
    # create the figure and plot the bar chart
    plt.figure(figsize=figsize)
    bars = plt.bar(data.index, data.values, color=color)
    
    # add value labels to each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # x position (center of the bar)
            height,  # y position (slightly above the bar)
            f'{height}',  # value label
            ha='center',  # horizontally center-aligned
            va='bottom',  # vertically bottom-aligned
            fontsize=10  # font size for labels
        )
    
    # set plot titles and labels
    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel(xlabel, fontsize=14, fontweight='bold')
    plt.ylabel('Frequency', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')  # rotate x-axis labels for better readability

    # adjust layout and show the plot
    plt.tight_layout()
    plt.show()


def plot_proportion(data, title, xlabel, color="skyblue", figsize=(8, 6)):
    """
    Plots a bar chart showing the percentage proportion of a given data distribution.

    :param data: pd.Series, a pandas Series containing the data to plot
    :param title: str, the title of the plot
    :param xlabel: str, the label for the x-axis
    :param color: str, the color of the bars (default: "skyblue")
    :param figsize: tuple, the size of the plot (default: (8, 6))
    :return: None
    """
    # calculate the proportion as percentages
    proportion = (data / data.sum()) * 100

    # create the figure and plot the bar chart
    plt.figure(figsize=figsize)
    bars = plt.bar(data.index, proportion.values, color=color)

    # add value labels to each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,  # x position (center of the bar)
            height,  # y position (slightly above the bar)
            f'{height:.2f}%',  # value label formatted as a percentage
            ha='center',  # horizontally center-aligned
            va='bottom',  # vertically bottom-aligned
            fontsize=10  # font size for labels
        )

    # set plot titles and labels
    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel(xlabel, fontsize=14, fontweight='bold')
    plt.ylabel('Percentage (%)', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')  # rotate x-axis labels for better readability

    # adjust layout and show the plot
    plt.tight_layout()
    plt.show()



def plot_gender_distribution_regions(data, title, bar_width=0.25, figsize=(10, 6)):
    """
    Plots gender distribution across America, Europe, and Both regions as percentages.

    :param data: pd.DataFrame, the dataset containing 'Continents' and 'Actor_Gender' columns
    :param title: str, the title of the plot
    :param bar_width: float, the width of the bars (default: 0.25)
    :param figsize: tuple, the size of the plot (default: (10, 6))
    :return: None
    """
    # define regions with filtering logic and corresponding colors
    regions = {
        "America": {"filter": lambda x: 'America' in x, "color": "skyblue"},
        "Europe": {"filter": lambda x: 'Europe' in x, "color": "lightgreen"},
        "Both": {"filter": lambda x: 'Both' in x, "color": "salmon"}
    }

    # define gender categories explicitly for consistent ordering
    all_categories = ['M', 'F']
    x_positions = np.arange(len(all_categories))
    positions = {region: x_positions + i * bar_width for i, region in enumerate(regions.keys())}

    # create the plot
    plt.figure(figsize=figsize)

    # process and plot data for each region
    for region, config in regions.items():
        # filter data for the current region
        region_data = data[data['Continents'].apply(config["filter"])]
        gender_counts = region_data['Actor_Gender'].value_counts()
        total_count = region_data['Actor_Gender'].count()

        # calculate percentages for all gender categories
        percentages = [(gender_counts.get(cat, 0) / total_count) * 100 for cat in all_categories]

        # plot bars for the region
        plt.bar(positions[region], percentages, width=bar_width, label=region, color=config["color"])

        # add percentage labels to bars
        for x, y in zip(positions[region], percentages):
            plt.text(x, y, f"{y:.1f}%", ha="center", va="bottom", fontsize=10)

    # customize plot appearance
    plt.title(title, fontsize=16, fontweight="bold")
    plt.xlabel("Gender", fontsize=14)
    plt.ylabel("Percentage (%)", fontsize=14)
    plt.xticks(x_positions + (len(regions) - 1) * bar_width / 2, all_categories)  # center gender labels
    plt.legend(title="Region")
    plt.tight_layout()

    # display the plot
    plt.show()



def get_svd_topics(components, vocab, top_words=12):
    """
    Extracts and displays the top words for each topic from SVD components.

    :param components: np.ndarray, the SVD components matrix where each row represents a topic
    :param vocab: list of str, the vocabulary corresponding to the matrix columns
    :param top_words: int, the number of top words to display for each topic (default: 12)
    :return: None
    """
    for idx, topic in enumerate(components):
        # extract the indices of the top 'n' words for the topic
        top_terms = [vocab[i] for i in topic.argsort()[-top_words:][::-1]]
        # display the topic and its top words
        print(f"Topic {idx + 1}: {' | '.join(top_terms)}")



def create_heatmap(continent, df):
    """
    Creates a heatmap showing the mean IMDb ratings for different comedy genres and rating categories in a specified continent.

    :param continent: str, the name of the continent (e.g., "America", "Europe")
    :param df: pd.DataFrame, the dataset containing 'Continents', 'comedy_genres', 'Rated', and 'Internet_Movie_Database_Rating' columns
    :return: None
    """
    # filter data for the specified continent
    continent_data = df[df['Continents'].apply(lambda x: continent in x)]
    
    # group by comedy genres and rating categories, then calculate the mean IMDb rating
    heatmap_data = continent_data.groupby(['comedy_genres', 'Rated'])['Internet_Movie_Database_Rating'].mean().unstack()
    
    # plot the heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(
        heatmap_data, 
        annot=True, 
        fmt=".1f", 
        cmap="YlGnBu", 
        cbar_kws={'label': 'Internet_Movie_Database_Rating'}
    )
    plt.title(f'Heatmap of IMDb Ratings for {continent}', fontsize=16, fontweight="bold")
    plt.xlabel('Rated', fontsize=14)
    plt.ylabel('Comedy Genres', fontsize=14)
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()
    plt.show()



ethnical_classification = {
    'African Descent or African': [
        'African Americans', 'Blackfoot Confederacy', 'Black Britons', 'African people', 'British African-Caribbean people', 'Berber', 'Yoruba people', 'Somalis', 
        'Mandinka people', 'Nigerian Americans', 'Afro-Cuban', 'Wolof people', 'Moroccans', 'Akan people', 'Sierra Leone Creole people', 'Kikuyu', 'Xhosa people', 
        'Haitian Americans'
    ],
    'European Descent and European': [
        'English people', 'Irish Americans', 'Italian Americans', 'White Americans', 'Scottish Americans', 'Irish people', 'Italians', 'Swedish Americans', 
        'German Americans', 'English Americans', 'Germans', 'White British', 'Irish migration to Great Britain', 'Russian Americans', 'Russians', 'Irish Canadians',
        'English Australian', 'Italian Canadians', 'White Latin American', 'White Africans of European ancestry', 'Anglo-Irish people', 'Italian Australians', 
        'Italians in the United Kingdom', 'Irish Australians', 'Italian Brazilians', 'Swedish Canadians', 'Scottish Australians', 'English Canadians', 
        'Swedish-speaking population of Finland', 'German Canadians', 'Dalmatian Italians', 'White South Africans', 'Italian immigration to Mexico', 
        'Baltic Russians', 'German Brazilians', 'Swedish Australian', 'Hispanic', 'French', 'Swedes', 'Welsh people', 'Dutch Americans', 'Spaniards',
        'Spanish Americans', 'Hungarian Americans', 'Greek Americans', 'Danes', 'Danish Americans', 'Romani people', 'French Americans', 'Australians', 'Americans',
        'Sicilian Americans', 'Norwegian Americans', 'Australian Americans', 'Croatian Canadians', 'Lithuanian Americans', 'British Americans', 'Slovak Americans',
        'Czech Americans', 'Portuguese Americans', 'French Canadians', 'Hungarians', 'Serbian Americans', 'Austrians',  'Albanian Americans', 'Czechs', 'Norwegians',
        'Polish Americans', 'Anglo-Celtic Australians', 'names of the Greeks', 'Welsh Americans', 'Swiss', 'Polish Canadians', 'Greek Canadians', 'Austrian Americans', 
        'Portuguese', 'Slovaks', 'French Chilean', 'Dutch Australian', 'Dutch Canadians', 'Polish Australians', 'Greek Cypriots', 'Greeks in the United Kingdom', 
        'Greeks in South Africa', 'Greek Australians', 'Croats', 'Croatian Americans', 'Ukrainians', 'Serbs in the United Kingdom', 'Latvians','Ukrainian Canadians', 
        'Bulgarians',  'Finns', 'Corsicans', 'Romanian Americans', 'Yugoslavs', 'Finnish Americans', 'Belarusians', 'Ukrainian Americans', 'Slavs', 'Danish Canadians', 'Serbs in North Macedonia',
        'Belgians', 'Serbs of Croatia', 'Albanians',  'Afrikaners', 'Serbs of Bosnia and Herzegovina',  'Bosnians', 'Romani people in Spain', 'Romanians', 'Bosniaks',
        'Cajun', 'Armenians', 'Croats', 'Sámi people', 'Georgians', 'Poles in the United Kingdom', 'Transylvanian Saxons', 'peoples of the Caucasus', 'Hutsuls',
        'Gibraltarian people', 'Slovenes',  'Quebeckers', 'Serbian Canadians', 'Slovene Americans', 'Catalans', 'Croatian Australians', 'Bulgarian Canadians', 
        'Galicians', 'Icelanders', 'Armenian Americans', 'Luxembourgish Americans', 'Aromanians', 'Manx people', 'Serbian Australians', 'Latvian Americans', 
        'Soviet people', 'Castilians', 'Armenians of Russia', 'Basque people', 'Romanichal', 'Ossetians', 'Bohemian People'
    ],
    'Jewish': [ 
        'Jewish people', 'American Jews', 'Ashkenazi Jews', 'British Jews', 'History of the Jews in Morocco', 'Sephardi Jews', 'history of the Jews in India', 'Lithuanian Jews', 
        'Israeli Jews', 'Israeli Americans', 'Israelis'
    ],
    'Asian Descent or Asian': [ 
        'Indians', 'Japanese people', 'Koreans', 'Chinese Americans', 'Indian Americans', 'Asian Americans', 'British Indian', 'Chinese Filipino', 'Nepali Indian', 
        'British Chinese', 'Korean Americans', 'Malaysian Chinese', 'Chinese Canadians', 'Chinese Singaporeans', 'Thai Chinese', 'Indian diaspora in France', 
        'Anglo-Indian people', 'Afro-Asians', 'British Asians', 'Indian Australian', 'Japanese Brazilians', 'Chinese Jamaicans', 'Chinese Indonesians', 'Indian diaspora', 
        'Punjabis', 'Hongkongers', 'Bengali', 'Filipino people', 'Filipino Americans', 'Vietnamese Americans', 'Vietnamese people', 'Filipino Australians', 'Filipino mestizo', 
        'Filipino people of Spanish ancestry', 'Thai Americans', 'Bengali Brahmins', 'Thai people', 'Pakistanis', 'Javanese', 'Taiwanese people', 'Sri Lankan Tamils', 
        'Zhuang people', 'Hindu', 'Sikh', 'Brahmin', 'Dalit', 'Lao people', 'Buryats', 'Azerbaijanis', 'Tamil', 'Malayali', 'Marathi people', 
        'Telugu people', 'Gujarati people', 'Kashmiri Pandit', 'Kayastha', 'Sindhis', 'Bunt (RAJPUT)', 'Nair', 'Pashtuns', 'Ezhava', 'Bihari people',
        'Jaat', 'Bhutia', 'Kannada people',  'Niyogi', 'Poles', 'Kashmiri people', 'Taiwanese Americans', 'Konkani people', 'Mudaliar', 'Sinhalese',
        'Rajput', 'Rohilla', 'Kapampangan people', 'Chettiar', 'Koryo-saram', 'Sherpa', 'Dogra', 'Gin people', 'Hazaras', 'Manchu', 'Agrawal', 'Tulu people', 
        'Hmong Americans', 'Aceh', 'Indonesian Americans', 'Marwari', 'Ilocano',  'Tibetan people', 'Khatri', 'Indo-Canadians', 'Ryukyuan people', 'Tatars'
    ],
    'Middle Eastern Descent or Middle Eastern': [ 
        'Arab Americans', 'Sudanese Arabs', 'Arabs in Bulgaria', 'Arabs', 'Persians', 'Arab Mexican', 'Lebanese Americans', 'Iranian peoples', 'Syrian Americans', 
        'Iranians in the United Kingdom', 'Iraqi Americans', 'Lebanese people', 'Palestinians in the United States', 'Iranian Americans', 'Iranian Canadians', 'Muslim', 
        'Assyrian people', 'مسح',  'Egyptians', 'Kurds', 'demographics of Iraq', 'culture of Palestine', 'Copts', 'Kabyle people',  'Muhajir'
    ],
    'Latin Descent or Latin': [
        'Mexican Americans', 'Mexicans', 'Puerto Ricans', 'Stateside Puerto Ricans', 'Latino', 'Lebanese Mexicans', 'Cuban Americans', 'Colombian Americans', 'Argentines', 
        'Chilean Americans', 'Colombians', 'Cubans', 'Salvadoran Americans', 'Chileans', 'Brazilian Americans', 'Brazilians', 'Chileans in the United Kingdom', 'Venezuelans',
        'Uruguayans', 'Ecuadorian Americans', 'Venezuelan Americans', 'Tejano', 'Dominican Americans', 'Honduran Americans', 'Bolivian Americans', 'Hondurans', 'Panamanian Americans'
    ],
    'Indegenous': [
        'Native Hawaiians', 'Cherokee', 'Mohawk', 'Inuit', 'Sioux', 'Iñupiaq people', 'Apache', 'Métis', 'Iroquois',  'Māori', 'First Nations', 'Aboriginal Australians',
        'Pacific Islander Americans', 'Malagasy people', 'Ho-Chunk', 'Oneida', 'Cheyennes', 'Nez Perce', 'Ojibwe', 'Choctaw', 'Samoan New Zealanders', 
        'Omaha Tribe of Nebraska'
    ],
    'Other': [
        'Parsi', 'Kiwi', 'Bahamian Americans', 'Turkish Americans', 'Cree', 'Lumbee', 'Spaniards in Mexico', 'Louisiana Creole people',  
        'Acadians', 'Dene', 'multiracial people', 'Aymara'
        ]
}


def map_ethnicity_to_hyperclass(ethnicity):
    """
    Maps a given ethnicity to its corresponding hyperclass based on predefined classifications.

    :param ethnicity: str, the name of the ethnicity to map
    :return: str, the corresponding hyperclass, or 'Not Found' if no match is found
    """
    # iterate through the ethnical classification dictionary
    for hyperclass, ethnicities in ethnical_classification.items():
        if ethnicity in ethnicities:
            return hyperclass

    # return 'Not Found' if no match is found
    return 'Not Found'


def map_ethnicity_list_to_hyperclass(ethnicity_list):
    """
    Maps a list of ethnicities to their corresponding hyperclasses.

    :param ethnicity_list: list of str, a list of ethnicities to map
    :return: list of str, the corresponding hyperclasses for each ethnicity
    """
    # map each ethnicity in the list to its hyperclass
    return [map_ethnicity_to_hyperclass(ethnicity) for ethnicity in ethnicity_list]



def casting(dataset_Genre_Cleaned, character_metadata, wikipedia_id=None):
    """
    Merges movie and character metadata, filters by Wikipedia ID, and returns a formatted DataFrame.

    :param dataset_Genre_Cleaned: pd.DataFrame, the dataset containing movie information
    :param character_metadata: pd.DataFrame, the dataset containing character metadata
    :param wikipedia_id: str or None, the Wikipedia ID of the movie to filter by (default: None)
    :return: pd.DataFrame or None, a formatted DataFrame with movie and actor information, or None if no data is found
    """
    # merge the datasets on Wikipedia_ID
    merged_df = pd.merge(dataset_Genre_Cleaned, character_metadata, on='Wikipedia_ID')

    # filter based on the provided Wikipedia ID
    if wikipedia_id:
        filtered_df = merged_df[merged_df['Wikipedia_ID'] == wikipedia_id]
    else:
        return None  # return None if no filters are provided

    # check if filtered_df is empty
    if filtered_df.empty:
        print(f"No data found for Wikipedia ID: {wikipedia_id}")
        return None  # return None if no matching rows are found

    # create a new DataFrame with the required format
    result_df = pd.DataFrame({
        'Movie_Name': [filtered_df['Movie_Name'].iloc[0]],
        'Wikipedia_ID': [filtered_df['Wikipedia_ID'].iloc[0]]
    })

    # add actor columns
    for i, (actor, ethnicity) in enumerate(zip(filtered_df['Actor_Name'], filtered_df['Actor_Large_Ethnicity']), start=1):
        result_df[f'Actor_Name_{i}'] = [actor]
        result_df[f'Actor_Ethnicity_{i}'] = [ethnicity]

    return result_df



def casting_ethnicity(casting_df):
    """
    Processes a casting DataFrame to count actor ethnicities and calculate totals.

    :param casting_df: pd.DataFrame, the input DataFrame containing actor ethnicity data
    :return: pd.DataFrame, the updated DataFrame with ethnicity counts and totals added as new columns
    """
    # define the possible ethnicity categories
    categories = [
        'African Descent or African', 
        'European Descent and European', 
        'Jewish', 
        'Asian Descent or Asian', 
        'Middle Eastern Descent or Middle Eastern', 
        'Latin Descent or Latin', 
        'Indegenous', 
        'Other'
    ]

    # calculate the total number of actors in the casting
    tot_count = (casting_df.shape[1] - 2) / 2

    # filter columns that match the pattern 'Actor_Ethnicity_i'
    ethnicity_columns = [col for col in casting_df.columns if col.startswith('Actor_Ethnicity_')]

    # flatten the values in these columns
    ethnicity_values = casting_df[ethnicity_columns].values.flatten()

    # calculate the total number of 'Not Found' values
    tot_nf = sum(value == 'Not Found' for value in ethnicity_values)

    # filter out 'Not Found' values
    filtered_values = [value for value in ethnicity_values if value != 'Not Found']

    # count occurrences of each ethnicity category
    counts = {category: 0 for category in categories}
    for value in filtered_values:
        if value in counts:
            counts[value] += 1
        else:
            counts['Other'] += 1  # count any other values as 'Other'

    # convert the counts dictionary to a list in the order of categories
    counts_list = [counts[category] for category in categories]

    # add the calculated values as new columns to the DataFrame
    casting_df['Ethnicity_List'] = [counts_list]
    casting_df['Total_Count'] = [tot_count]
    casting_df['Total_Not_Found'] = [tot_nf]

    return casting_df


def diversity_score(casting_df):
    """
    Calculates a diversity score based on actor ethnicities in the casting DataFrame.

    The diversity score is computed using entropy, which considers the proportions
    of ethnicities among actors (excluding 'Not Found').

    :param casting_df: pd.DataFrame, the input DataFrame containing ethnicity data
                       and precomputed totals ('Ethnicity_List', 'Total_Not_Found', 'Total_Count')
    :return: float or None, the diversity score or None if the score cannot be calculated
    """
    # check if casting_df is empty
    if casting_df is None:
            return None  # return None if casting_df is empty
    else:
        count,nf,N=casting_df['Ethnicity_List'].iloc[0], casting_df['Total_Not_Found'].iloc[0], casting_df['Total_Count'].iloc[0]
        if N<=1:
            print(f"No diversity score to be made with only 1 actor ({casting_df['Wikipedia_ID']})")
            return None
        elif N-nf<2:
            print(f"No diversity score to be made with only less than 2 actor ethnicities ({casting_df['Wikipedia_ID']})")
            return None
        else:
            proportions=[c/(N-nf) for c in count]
            score=stats.entropy(proportions,base=8)

            
            return score

