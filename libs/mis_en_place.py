import pandas as pd
import numpy as np
import configparser
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
from nltk.stem.snowball import SnowballStemmer

def removeStopwords(meal_component):
    if pd.notna(meal_component):
        stop_words = stopwords.words('german')

        config = configparser.ConfigParser()
        config.read('config.ini')
        user_stopwords = [str(x) for x in config['preprocessing']['Stopwords'].split(', ')]
        # user_stopwords = ['new', 'words']
        
        
        for i in user_stopwords:
            stop_words.append(i)

        stop_words = set(stop_words)

        tokens = word_tokenize(meal_component)
        filtered = [w for w in tokens if not w in stop_words]
        meal_component = ' '.join(filtered)
        
    return meal_component

def removeBrackets(meal_component):
    if not pd.isna(meal_component):
        meal_component = meal_component.replace(r"\s*\(.*\)\s*", "")
        meal_component = meal_component.replace("( ", "")
        meal_component = meal_component.replace(" )", "")
        meal_component = meal_component.replace(r"\s*\[.*\]\s*", "")
        meal_component = meal_component.replace(r"\s*\{.*\}\s*", "")
        return meal_component

def removeApostrophes(meal_component):
    if not pd.isna(meal_component):
        meal_component = meal_component.replace('"', "")
        meal_component = meal_component.replace("'", "")
        meal_component = meal_component.replace("`", "")
        meal_component = meal_component.replace('" ', "")
        meal_component = meal_component.replace("' ", "")
        meal_component = meal_component.replace("` ", "")
        meal_component = meal_component.replace(' "', "")
        meal_component = meal_component.replace(" '", "")
        meal_component = meal_component.replace(" `", "")
        return meal_component

def removePunctuation(meal_component):
    if not pd.isna(meal_component):
        meal_component = meal_component.replace("*", "")
        meal_component = meal_component.replace(",", "")
        meal_component = meal_component.replace(".", "")
        meal_component = meal_component.replace("/", "")
        meal_component = meal_component.replace("+", "")
        meal_component = meal_component.replace("#", "")
        meal_component = meal_component.replace(":", "")
        meal_component = meal_component.replace("&", "")
        meal_component = meal_component.replace("-", "")
        return meal_component

def cleanSpaces(meal_component):
    if not pd.isna(meal_component):
        meal_component = meal_component.replace(r"- ", "-")
        meal_component = meal_component.replace(r" -", "-")
        meal_component = meal_component.replace(r"  ", " ") #double spaces to single space
    return meal_component

def mealStemmer(meal_component):
    if not pd.isna(meal_component):
        stemmer = SnowballStemmer("german")
        return stemmer.stem(meal_component)

def mixComponents(data):
    # If a meal_component is removed by stopword filtering: replace the empty cell with NaN
    data = data.replace(r'^\s*$', np.nan, regex=True)
    
    data = data.dropna()
    menus = data.groupby(['date', 'meal_line', 'tot_sold'])['meal_component'].apply(lambda x: "%s" % ' '.join(x))
    menus = pd.DataFrame(menus).reset_index(level=['meal_line', 'tot_sold'])
    menus = menus.astype({'tot_sold': int})
    menus.meal_component = menus.meal_component.apply(cleanSpaces)
    return menus