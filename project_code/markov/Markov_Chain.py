import collections
import numpy as np
import pandas as pd
import itertools

def unlist_Items(clauses, clause_states=True):    
    # Input: list of lists with abstracted text elements. 
    # clause_states is a TRUE/FALSE value that indicates whether states should be added
    # Output: unlisted transitions.
    if not clause_states:
        return list(itertools.chain(*clauses))
    transitions = list()
    for clause in clauses:
        transitions.append("Clause_Begin")
        transitions.extend(clause)
        transitions.append("Clause_End")
    return transitions
        
def transitionMatrix(feature_dict, clause_states=True):
    # Input: feature_dict
    # Output: transition frequency matrix
    
    df_Transition_freq = dict() # Transition matrix with frequences

    for bookname, clauses in feature_dict.items(): 
        transitions = unlist_Items(clauses, clause_states)
        nodes = list(set(transitions))
        transition_Matrix = np.zeros((len(nodes),len(nodes)))
        
        for i in range(0, len(transitions)-1):
            state1 = nodes.index(transitions[i])
            state2 = nodes.index(transitions[i+1])
            transition_Matrix[state1,state2] +=1 
        
        df_Transition_freq[bookname] = pd.DataFrame(transition_Matrix, index=nodes, columns=nodes)
            
    return df_Transition_freq

def countTransitions(Transition_freq):
    Transitions = dict()
    for bookname, df in Transition_freq.items(): 
        Transitions[bookname] = np.sum(df.sum())
    return Transitions

def averageTransformation(Transition_freq):
    nTransitions = 0
    for bookname, df in Transition_freq.items(): 
        nTransitions = nTransitions + df.sum().sum()
    mean = nTransitions / len(Transition_freq.keys())
    
    Transition_average = dict() 
    for bookname, df in Transition_freq.items(): 
        Transition_average[bookname] = df.div(df.sum()) * mean 
    return Transition_average
        
def MCTransformation(Transition_freq):
    Transition_prob = dict() 
    for bookname, df in Transition_freq.items(): 
        Transition_prob[bookname] = df.div(df.sum(axis=1), axis=0) 
    return Transition_prob
    
def df_dict_Transformation(Transition_freq):
    dict_Transitions = collections.defaultdict(dict)
    for bookname, df in Transition_freq.items(): 
        dictionary = df.to_dict(orient='split')
        for i in range(1,len(dictionary["index"])):
            for j in range(1,len(dictionary["columns"])):
                statei = dictionary["index"][i]
                statej = dictionary["index"][j]
                transition = statei + "->" +  statej
                value = dictionary["data"][i][j]   
                dict_Transitions[bookname][transition] = value
    return dict_Transitions

def stackTransitions(Transition_Dicts, feature, domain):          
    stacked_df = pd.DataFrame()
    for l in feature:
        for d in domain:
            stacked_df = stacked_df.append(Transition_Dicts[l][d])
    return stacked_df.fillna(0)
    
