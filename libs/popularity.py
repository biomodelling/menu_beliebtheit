import pandas as pd
import numpy as np

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
