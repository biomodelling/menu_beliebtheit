import pandas as pd
import numpy as np
from sklearn.preprocessing import KBinsDiscretizer

def basic_popularity(data):
    """
    Menu popularity for each component

    Args:
    data:   DataFrame with preprocessed selling data

    returns:
    df with popularity as a probability for selling a certain menu 
    component given the selection at this day.
    """
    popularity = data.copy()
    for index, row in data.iterrows():
        popularity.loc[index] = row/row.sum()
    return popularity

def weight_of_day(df):
    """
    Weighting of the line total. 
    Days with many menus sold, this should be weighted heavier.

    Args:
    data:   DataFrame with preprocessed selling data

    returns:
    df with weight per day.
    """
    wgt_day = pd.DataFrame(np.nan, index=df.index, columns=["wgt"])
    total_sold_menus = df.fillna(0).values.sum()
    print(total_sold_menus)
    for index, row in df.iterrows():
        wgt_day.loc[index] = row.sum()/total_sold_menus
    # return pd.DataFrame(wgt_day, index=data.index, columns=["wgt"])
    return wgt_day

def weighted_popularity(bp, wod):
    """
    Calculates the popularity weighted by the probability that the meal is even
    sold at that day.

    Args:
    basic_popularity:   DataFrame with probabilities selling a menu component in the provided choice
    weigth_of_day:      DataFrame with daily weights

    returns:
    df with weighted average of selling probability 
    """

    x = bp.values * wod.values
    y = pd.DataFrame(x, index=bp.index, columns=bp.columns)
    #wgt_pop_mL = y.sum(axis=1) # returns also meal_label
    wgt_pop = y.sum(axis = 0)
    
    return wgt_pop

def popularity_classification(wgt_pop, n_bins=5, encode='ordinal', strategy='quantile'):
    """"
    Discretize continuous popularity probability into intervals (Feature Binarization).
    
    Args:
    wgt_pop:    df. Output from calc_popularity()
    nbins:      int. Number of classes/bins
    encode:     'onehot', 'onehot-dense', 'ordinal' where the latest returns the bin identifier encoded as an integer value.
    strategy:   'uniform', 'kmeans', 'quantile' where the latest distributes all points equally between the bins (all bins have equal amount of points).
    
    Returns:
    df with popularity and popularity_class
    """
    # extract popularity-values as 1D vector
    X = np.array(wgt_pop).reshape(-1,1)

    # Configure and fit Binarizer
    enc = KBinsDiscretizer(n_bins=n_bins, encode=encode, strategy=strategy)
    enc.fit(X)
    x_encoded = pd.DataFrame(enc.transform(X))
    
    # Append the bin-identifier as additional row to the original dataframe
    wgt_pop_df = pd.DataFrame(wgt_pop.copy())
    wgt_pop_df['popularity_class'] = [int(x)+1 for x in x_encoded.values] # +1 to start at 1 and not 0
    
    return wgt_pop_df
