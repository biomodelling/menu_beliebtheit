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
    # Combine menu components to menu
    # ----------------
    data = mep.mixComponents(data)
    print("mixed menus \n", data.head())

    # ----------------
    # Bring data in specified Form
    # ----------------
    df = data.pivot_table(index='date', columns='meal_component', values='tot_sold')
    print("That's how we need the data \n", df.head())

    # ----------------
    # Store preprocessed dataframe
    # ----------------
    if save == True:
        df.to_csv('./data/preprocessed.csv')
    else:
        return df

def preprocess_choice(data):
    """
    Same preprocessing as with the already known meals.
    """
    # data = pd.DataFrame(data)
    # ----------------
    # Remove stopwords
    # ----------------
    data = [mep.removeStopwords(x) for x in data]
    print("Removed stopwords \n", data[:5])

    # ----------------
    # Remove Parentheses
    # ----------------
    data = [mep.removeBrackets(x) for x in data]
    print("Removed Parentheses \n", data)

    # ----------------
    # Remove Parentheses
    # ----------------
    data = [mep.removeApostrophes(x) for x in data]
    print("Removed Apostrophes \n", data)

    # ----------------
    # Clean Spaces
    # ----------------
    # Lachs im Oliven-Kräutermantel	Lachs mit Oliven- Kräutermantel	Lachs mit Oliven-Kräutermantel
    #Karotten	Karotten Duo	Karotten- Duo	Karotten-Duo
    data = [mep.cleanSpaces(x) for x in data]
    print("Cleaned spaces \n", data)

    # ----------------
    # Stemming
    # ----------------
    #Pappardelle	Pappardellen
    data = [mep.mealStemmer(x) for x in data]
    print("Stemmed meals \n", data)

    # ----------------
    # Lemmatization
    # ----------------
    # TODO: No german lemmatizer available...

    return data

def flatten(lst):
	return sum( ([x] if not isinstance(x, list) else flatten(x)
		     for x in lst), [] )

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

def known_menu_combination(df_processed, choice_processed):
        counter = 0

        for day in range(df_processed.shape[0]):
            d = df_processed.iloc[day,:].dropna()
            x = list()
            for i in d.index:
                x.append(i.split(' '))

            x = flatten(x)

            cho = flatten([elem.split(' ') for elem in choice_processed])

            if all(elem in x for elem in cho):
                counter += 1

        if counter>0:
            print("combination already known")
            return True
        elif counter == 0:
            print("combination not yet seen.")
            return False
        # TODO: check if the single menus have been seen and just the choice is new.

def get_popularity_index(wgt_pop, choice_processed, num_comp_per_dish):
    wgt_pop = wgt_pop.reset_index()

    prev_num_comp = 0
    selection = pd.DataFrame(np.nan, index = range(len(num_comp_per_dish)), columns=['meal_component', 'popularity'])

    #TODO: Bug here: if more than 2 dishes provided, doesn't work!
    for j in range(len(num_comp_per_dish)):
        num_comp = prev_num_comp+num_comp_per_dish[j]
        for i in range(len(wgt_pop.meal_component)): 
            if wgt_pop.iloc[i,0] == ' '.join(choice_processed[prev_num_comp:num_comp]): 
                selection.iloc[j,0] = wgt_pop.iloc[i,0]
                selection.iloc[j,1] = wgt_pop.iloc[i,1]
                
                prev_num_comp = sum(num_comp_per_dish[:j])

    return selection 

def known_dishes_new_combination(choice_processed, num_comp_per_dish):
    wgt_pop = calc_popularity(df_processed)
    # check if dishes are known
    # get all dishes provided
    combo_pop = get_popularity_index(wgt_pop, choice_processed, num_comp_per_dish)
    # see if combo_pop in wgt_pop
    # TODO: Continue here....
    
    
    # wgt_pop[wgt_pop.index in combo_pop.loc['meal_component']]
    
    # # dishes are already known
    # if ():
    #     return True
    
    # else:
    #     return False
#################
# 
if __name__ == "__main__":
    # Load raw_data
    raw_data = pd.read_csv(glob.glob('./data/raw_data/*.csv')[0], parse_dates=True, index_col=0, keep_default_na=True)
    print("Raw data \n", raw_data.head())

    # Provide a dish combination
    # choice = ["Quornschnitzel", "Morchelsauce", "Basmatireis", "Salat", "Kalbssteak", "Morchelsauce", "Griessgnocchi", "Grüne Bohnen"]
    # num_comp_per_dish = [4, 4]
    choice = ["appenzeller cordon bleu", "zitronenschnitz", "pommes frit", "salat", "Quornschnitzel", "Morchelsauce", "Basmatireis", "Salat", "Kalbssteak", "Morchelsauce", "Griessgnocchi", "Grüne Bohnen"]
    num_comp_per_dish = [4, 4, 4]

    # Preprocess
    df_processed = preprocess_meal(raw_data, save=False)
    choice_processed = preprocess_choice(choice)
    print(df_processed)
    print(choice_processed)
    
    # Check if already known combination is provided
    if known_menu_combination(df_processed, choice_processed):
        wgt_pop = calc_popularity(df_processed)
        print("Top 20 meals: \n", wgt_pop[:20])

        combo_pop = get_popularity_index(wgt_pop, choice_processed, num_comp_per_dish)
        print("The popularity of the first provided menu in this combination is: \n", combo_pop)
    elif known_dishes_new_combination(choice_processed, num_comp_per_dish):
        
        print("The popularity of this new combination of already known dishes is: \n", 'foo')
    
    else:
        print("You provided an unknown dish. \nThis algorithm is not yet implemented.")
