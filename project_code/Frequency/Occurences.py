import collections
from itertools import chain
import pandas as pd

def make_counts(feature_dict):
    feature_count = dict() # counts here

    # loop and count
    for bookname, units in feature_dict.items():
        feature_count[bookname] = collections.Counter(list(chain(*units))) 

    # make into dataframe
    df_Count = pd.DataFrame(feature_count, columns=feature_dict.keys()).fillna(0)
    
    # return both count and probability objects
    return  df_Count

def transformAverage(df_Count):
    df_mean = df_Count.sum().mean()
    return df_Count.apply(lambda col: col * df_mean / col.sum())