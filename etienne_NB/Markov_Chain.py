import pandas as pd
import collections
import itertools
import numpy as np
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
        
        df_Transition_freq[bookname] = pd.DataFrame(transition_pairs, index=nodes, columns=nodes)
            
    return df_Transition_freq







def make_stacked_transitions(data_dict):
    '''
    --input--
    output from bhsa.get_data()
    i.e. dict[feature][domain][book] = list(list(strings))
    
    --output--
    x2 df(trans. frequencies x book), df(trans. ratios x book)
    stacked for all features/domains by book
    '''
    
    freq_matrices = {}
    norm_matrices = {}
    
    for feature, domains in data_dict.items():    
        for domain in domains:
            
            clause_ends = True if feature != 'clause_types' else False
            
            # add all data together
            data = data_dict[feature][domain]
            name = feature+'|'+domain
            trans_freq, trans_norm = make_transitions(data, clause_ends)
            
            # save to dicts
            freq_matrices[name] = trans_freq
            norm_matrices[name] = trans_norm           
        
    stacked_freq = pd.DataFrame()
    stacked_norm = pd.DataFrame()
        
    # make the frequency stacked matrices
    for data_name, matrix in freq_matrices.items():
        stacked_freq = stacked_freq.append(matrix)

    # make the normalized stacked matrices
    for data_name, matrix in norm_matrices.items():
        stacked_norm = stacked_norm.append(matrix)
    
    return stacked_freq.fillna(0), stacked_norm.fillna(0)