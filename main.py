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
import getopt
import configparser

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
config = configparser.ConfigParser()
config.read('config.ini')
POOL_RAW_DATA = config['paths']['input_triemli']
# POOL_RAW_DATA = config['paths']['input_erz']
# POOL_RAW_DATA = config['paths']['input_waid']

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
        # if there is no raw data file, load it from server
        load_menu.pool2data(POOL_RAW_DATA)
    else:
        print('There is already a raw data file. No copy performed.')
else:
    raise ValueError('Some issue with setting up the directory structure.')



# ----------------
# Preprocess
# ----------------
def preprocess_meal(data, save):
    """
    Basic NLP Preprocessing incl. some specific cleaning for this data. 

    Args:
    raw_data:   DataFrame with selling information.
    save:       Bool (True) as long format - important to add additional variable e.g. meal label 
                If False the df as pivoted DataFrame is returned

    Returns (only when save = False):
    Cleaned and pivoted DataFrame as .csv
    """
    # ----------------
    # Check data format
    # ----------------
    if not "meal_component" in data.columns:
        sys.exit("Wrong header in input file.")

    # ----------------
    # Remove stopwords
    # ----------------
    data.meal_component = data.meal_component.apply(mep.removeStopwords)
    print("Removed stopwords \n", data.head(2))

    # ----------------
    # Remove Parentheses
    # ----------------
    data.meal_component = data.meal_component.apply(mep.removeBrackets)
    print("Removed Parentheses \n", data.head(2))

    # ----------------
    # Remove Apostrophes
    # ----------------
    data.meal_component = data.meal_component.apply(mep.removeApostrophes)
    print("Removed Apostrophes \n", data.head(2))
    
    # ----------------
    # Remove Parentheses
    # ----------------
    data.meal_component = data.meal_component.apply(mep.removePunctuation)
    print("Removed Punctuation \n", data.head(2))

    # ----------------
    # Clean Spaces
    # ----------------
    # Lachs im Oliven-Kräutermantel	Lachs mit Oliven- Kräutermantel	Lachs mit Oliven-Kräutermantel
    #Karotten	Karotten Duo	Karotten- Duo	Karotten-Duo
    data.meal_component = data.meal_component.apply(mep.cleanSpaces)
    print("Cleaned spaces \n", data.head(2))

    # ----------------
    # Stemming
    # ----------------
    #Pappardelle	Pappardellen
    data.meal_component = data.meal_component.apply(mep.mealStemmer)
    print("Stemmed meals \n", data.head(2))

    # ----------------
    # Lemmatization
    # ----------------
    # TODO: No german lemmatizer available...

    # ----------------
    # Combine menu components to menu
    # ----------------
    data = mep.mixComponents(data)
    print("mixed menus \n", data.head(2))

    # ----------------
    # Bring data in specified Form
    # ----------------
    df_wide = data.pivot_table(index=['date'], columns='meal_component', values='tot_sold')
    print("That's how we need the data \n", df_wide.head(2))

    # ----------------
    # Store preprocessed dataframe as long and not pivoted format
    # ----------------
    if save == True:
        data.to_csv('./data/preprocessed_long', sep = ",")
        return data
    else:
        return df_wide

# It's used to handle the data structure in known_menu_combination()
def flatten(lst):
	return sum( ([x] if not isinstance(x, list) else flatten(x)
		     for x in lst), [] )

# ----------------
# Popularity
# ----------------
def calc_popularity(data_preprocessed):
    popularity = popular.basic_popularity(data_preprocessed)

    # weighting of day (row total)
    wgt_day = popular.weight_of_day(data_preprocessed)
    
    # Weighted Popularity
    wgt_pop = popular.weighted_popularity(popularity, wgt_day)
    return wgt_pop.sort_values(ascending = False)

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
    """
    Extracts the popularity of the provided dishes from the already known menu combinations

    Args:
    wgt_pop:            DataFrame with populartity of already known menu combinations
    choice_processed:   List of Strings with preprocessed menu components.
    num_comp_per_dish:  List of int with number of menu components of each menu.

    returns:
    DataFrame with the popularity of the menus in the given combination
    """
    # df with populartity of already known menu combinations to dict for fast accessing menu comp.
    wgt_pop = wgt_pop.to_dict()

    # set counter for slicing the input list of menu components
    prev_num_comp = 0

    # initialize dataframe for return of selected menu components
    selection = pd.DataFrame(np.nan, index = range(len(num_comp_per_dish)), columns=['meal_component', 'popularity'])

    for j in range(len(num_comp_per_dish)):
    # Iterate through all input dishes
        # j: index in list of number of menu components
        # num_comp: number of menu components 
        num_comp = prev_num_comp+num_comp_per_dish[j]
        
        # select the input menu
        key_menu = ' '.join(choice_processed[prev_num_comp:num_comp])

        # fill return of selected menu components
        selection.iloc[j,0] = key_menu
        selection.iloc[j,1] = wgt_pop.get(key_menu)
        
        # step forward with the counter for slicing the input menu components
        prev_num_comp = num_comp # or: sum(num_comp_per_dish[:j]) ?

    return selection 

def known_dishes_new_combination(choice_processed, num_comp_per_dish):
    # Preprocess all known dishes and calculate their popularity
    wgt_pop = calc_popularity(df_processed)
    wgt_pop_lst = list(wgt_pop.index)
    
    # Preprocess the provided, already known dishes
    combo_pop = get_popularity_index(wgt_pop, choice_processed, num_comp_per_dish)
    combo_pop_lst = list(combo_pop.iloc[:,0])

    # Check if all of the provided dishes are already known
    known_combo = 0
    for combo in combo_pop_lst:
        if combo in wgt_pop_lst:
            known_combo +=1
    
    if known_combo == len(combo_pop_lst):
        return True
    else:
        return False
    
def calc_popularity_new_combo(df_processed, choice_processed, num_comp_per_dish):
    wgt_pop = calc_popularity(df_processed)
    combo_pop = get_popularity_index(wgt_pop, choice_processed, num_comp_per_dish)

    new_combo_pop = combo_pop.copy() # initialize new DataFrame
    
    for index, row in new_combo_pop.iterrows():
        new_combo_pop.iloc[index, 1] = row[1] / combo_pop.iloc[:,1].sum()

    return new_combo_pop


if __name__ == "__main__":
    # Load raw_data
    raw_data_file = glob.glob('./data/raw_data/*.csv')
    raw_data_file.sort()
    raw_data_file = raw_data_file[0] # 0: all 1: erz, 2: triemli, 3: waid
    print("Raw data file\n", raw_data_file)
    raw_data = pd.read_csv(raw_data_file, sep = ",", parse_dates=True, index_col=0, keep_default_na=True)
    print("Raw data \n", raw_data.head())

    # Read arguments:
    try:
        opts, args = getopt.getopt(sys.argv[1:],"o:n:",["output-format=", "file-name="])
    except getopt.GetoptError:
        print("python3 main.py -o <file>/<input> -n <file-name>")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-o", "--output-format"):
            out_form = arg
        elif opt in ("-n", "--file-name"):
            filename = arg
            filename_merge = filename[:-4]+"_add_vars.csv"

    # For debuging:
    out_form = "file"
    filename = "popularity_all_debug.csv"
    filename_merge = "merge_add_vars_debug.csv"

    if out_form == "file":
        """
        Calculates the likelihood of selling Menu M_i given the set of offered menus (menu choice). 
        This can be a direct measure for the menu popularity.
        """
        # Preprocess
        SAVE_PREPROCESS = bool(config['preprocessing']['save_preprocessing'])
        df_processed_long = preprocess_meal(raw_data, save=SAVE_PREPROCESS)
        df_processed_wide = df_processed_long.pivot_table(index=['date'], columns='meal_component', values='tot_sold')

        # menu component popularity 
        try:
            if df_processed_wide.empty:
                raise Exception("Preprocessed data not stored in Workspace, only saved to file.")
            else:
                wgt_pop = calc_popularity(df_processed_wide)
                print("Top 20 meals: \n", wgt_pop[:20])
        except Exception as e:
            sys.exit("Error in preprocessing: {0}".format(e))

        try:
            # Binarize popularity in classes facilitates interpretation
            wgt_pop = popular.popularity_classification(wgt_pop, n_bins=10, encode='ordinal', strategy='quantile')
            
            wgt_pop = wgt_pop.reset_index()
            wgt_pop.columns = ['meal_component', 'popularity', 'popularity_class']

            wgt_pop.to_csv("./data/"+filename, header=True, index=False, columns = ['meal_component', 'popularity', 'popularity_class'])
            print("1) Meal popularity saved into file:", "./data/"+filename)
            
            # Add additional variables facilitating menu retrieval.
            ADDITIONAL_VARIABLES = bool(config['output']['additional_variables'])
            if ADDITIONAL_VARIABLES == True:
                df_merged = pd.merge(wgt_pop[["meal_component", "popularity"]], df_processed_long.reset_index()[["meal_label", "meal_component", "date", "source"]], how = "left", on = "meal_component")
                df_merged.to_csv("./data/"+filename_merge, header=True, index=False)
                print("2) Meal popularity **WITH** three add variables: meal_label, date and source saved into file:", "./data/"+filename_merge)
                
            elif ADDITIONAL_VARIABLES == False:
                print("2) Meal popularity is saved **WITHOUT** additional variables into", ".data/"+filename)  
                
        except NameError as e:
            print("Failed writing file. Please provide a valid filename as argument.") 

    
    elif out_form == "input":
        """
        Calculates the likelihood of selling Menu M_i given a set of offered menus as input.
        if this menu combination already appeared:
            return it's popularity based on experience
        if each of the menus itself did appear already in a known set but the menu combination is new:
            return the probability of this new combination
        if the menu is new:
            return a message that this is not yet implemented.
        """        
        print("INFO: The Input menu combination is provided within the script and not by user input.")

        # Provide a known dish combination
        print("known dish combination of known dishes is provided.")
        choice = ["Quornschnitzel", "Morchelsauce", "Basmatireis", "Salat", "Kalbssteak", "Morchelsauce", "Griessgnocchi", "Grüne Bohnen"]
        num_comp_per_dish = [4, 4]

        # Provide a new, unknown dish combination of known dishes
        # print("new, unknown dish combination of known dishes is provided.")
        # choice = ["appenzeller cordon bleu", "zitronenschnitz", "pommes frit", "salat", "Quornschnitzel", "Morchelsauce", "Basmatireis", "Salat", "Kalbssteak", "Morchelsauce", "Griessgnocchi", "Grüne Bohnen"]
        # num_comp_per_dish = [4, 4, 4]

        # Preprocess
        df_processed = preprocess_meal(raw_data, save=False)
        print("----------------------------------------------------------------------------------")
        choice_processed = preprocess_choice(choice)
        print("----------------------------------------------------------------------------------")

        # Check if already known combination is provided
        if known_menu_combination(df_processed, choice_processed):
            wgt_pop = calc_popularity(df_processed)
            print("Top 20 meals: \n", wgt_pop[:20])

            combo_pop = get_popularity_index(wgt_pop, choice_processed, num_comp_per_dish)

            new_combo_pop = combo_pop.copy() # initialize new DataFrame
            for index, row in new_combo_pop.iterrows():
                new_combo_pop.iloc[index, 1] = row[1] / combo_pop.iloc[:,1].sum()


            print("The popularity of the first provided menu in this combination is: \n", new_combo_pop)

        elif known_dishes_new_combination(choice_processed, num_comp_per_dish):
            new_combo_pop = calc_popularity_new_combo(df_processed, choice_processed, num_comp_per_dish)
            
            print("The popularity of this new combination of already known dishes is: \n", new_combo_pop)
        
        else:
            print("You provided an unknown dish. \nThis algorithm is not yet implemented.")

 