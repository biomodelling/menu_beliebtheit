#!/usr/bin/python3
"""
(C) Matteo Delucchi, 2020
return: csv with beliebtheit for each menu

"""
import sys
import os
import glob
import pandas as pd 
import numpy as np

#################
# Housekeeping
#################
# Add lib folder to python path
sys.path.append('./libs')

# import specific modules
import load_menu
import mis_en_place as mep
import popularity as popular

# ----------------
# Parameters
# ----------------
#TODO: put this in config.ini
POOL_RAW_DATA = "/mnt/zhaw_s/N-IUNR-FP-1-23-Stadt-Zuerich/07 Verkaufszahlen PR/selling_data_PR/menu_till_data_stadt_zh/augmented data/sellings_triemli_2019_200119_egel.csv"

# ----------------
# Prepare directory structure
# ----------------
if not os.path.exists('./data/raw_data'):
    # make data directory
    os.mkdir('./data/raw_data')
    # copy raw data to data directory
    load_menu.pool2data(POOL_RAW_DATA)
elif os.path.exists('./data/raw_data/'):
    if not os.listdir('./data/raw_data/'):
        # if there is already a raw data file
        load_menu.pool2data(POOL_RAW_DATA)
    else:
        print('There is already a raw data file. No copy performed.')
else:
    raise ValueError('Some issue with setting up the directory structure.')



#################
# Preprocess
#################
def preprocess_meal(data, save=True):
    """
    Basic NLP Preprocessing incl. some specific cleaning for this data. 

    Args:
    raw_data:   DataFrame with selling information.
    save:       Bool (True). If False the df is returned

    Returns:
    Saves cleaned and pivoted DataFrame as .csv
    """
    # ----------------
    # Remove stopwords
    # ----------------
    data.meal_component = data.meal_component.apply(mep.removeStopwords)
    print("Removed stopwords \n", data.head())

    # ----------------
    # Remove Parentheses
    # ----------------
    data.meal_component = data.meal_component.apply(mep.removeBrackets)
    print("Removed Parentheses \n", data.head())

    # ----------------
    # Remove Parentheses
    # ----------------
    data.meal_component = data.meal_component.apply(mep.removeApostrophes)
    print("Removed Apostrophes \n", data.head())

    # ----------------
    # Clean Spaces
    # ----------------
    # Lachs im Oliven-Kräutermantel	Lachs mit Oliven- Kräutermantel	Lachs mit Oliven-Kräutermantel
    #Karotten	Karotten Duo	Karotten- Duo	Karotten-Duo
    data.meal_component = data.meal_component.apply(mep.cleanSpaces)
    print("Cleaned spaces \n", data.head())

    # ----------------
    # Stemming
    # ----------------
    #Pappardelle	Pappardellen
    data.meal_component = data.meal_component.apply(mep.mealStemmer)
    print("Stemmed meals \n", data.head())

    # ----------------
    # Lemmatization
    # ----------------
    # TODO: No german lemmatizer available...

    # ----------------
    # Make bag of words
    # ----------------
    bow = mep.bag_of_menu(data)

    # # ----------------
    # # Bring data in specified Form
    # # ----------------
    # df = data.pivot_table(index='date', columns='meal_component', values='tot_sold')
    # print("That's how we need the data \n", df.head())

    # # ----------------
    # # Store preprocessed dataframe
    # # ----------------
    # if save == True:
    #     df.to_csv('./data/preprocessed.csv')
    # else:
    #     return df


#################
# Popularity
#################
def calc_popularity(data_preprocessed):
    popularity = popular.basic_popularity(data_preprocessed)

    # weighting of day (row total)
    wgt_day = popular.weight_of_day(data_preprocessed)
    
    # Weighted Popularity
    wgt_pop = popular.weighted_popularity(popularity, wgt_day)
    return wgt_pop.sort_values( ascending = False)

#################
# 
if __name__ == "__main__":
    # Load raw_data
    raw_data = pd.read_csv(glob.glob('./data/raw_data/*.csv')[0], parse_dates=True, index_col=0, keep_default_na=True)
    print("Raw data \n", raw_data.head())
    # Preprocess
    df_processed = preprocess_meal(raw_data[:20], save=False)
    # menu component popularity 
    # df_processed = pd.DataFrame([[1, 2, 3], [4,5,6]])
    print(df_processed)

    # wgt_pop = calc_popularity(df_processed)
    # print(wgt_pop[:20])
    
