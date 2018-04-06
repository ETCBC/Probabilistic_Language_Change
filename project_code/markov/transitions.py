import pandas as pd
import collections

def make_transitions(feature_dict):
    '''
    --input--
    feature dictionary
    dict[book] = list(list(strings))
    
    --output--
    x2 df(transition frequencies), df(transition ratios)
    '''
    
    df_Transition_freq = dict() # Transition matrix with frequences
    df_Transition_prob = dict() # Normalized transition matrix

    # a dict to count the transition pairs per book
    transition_pairs = collections.defaultdict(lambda: collections.Counter())
    
    for bookname, clauses in feature_dict.items():
        
        # count transitions using bigrams
        transitions = list()
        for clause in clauses:
            transitions.append("Clause_Begin")
            transitions.extend(clause)
            transitions.append("Clause_End")
            
        for i in range(0, len(transitions)-1):
            
            # assemble transition pair string
            state1 = transitions[i]
            state2 = transitions[i+1]
            transition_string = state1 + '->' + state2
            
            if transition_string == 'Clause_End->Clause_Begin': # ignore clause_begin to end transition pairs
                continue 
            
            transition_pairs[bookname][transition_string] += 1
            
        # create the dataframes
        df_trans = pd.DataFrame(transition_pairs).fillna(0)
        df_prop = df_trans.apply(lambda column: column.values / sum(column.values))
        
    return df_trans, df_prop

def make_stacked_transitions(data_dict):
    '''
    --input--
    output from bhsa.get_data()
    i.e. dict[feature][domain][book] = list(list(strings))
    
    
    --output--
    x2 dict(transition frequencies), dict(transition ratios)
    stacked for all features/domains by book
    '''
    
    freq_matrices = {}
    prop_matrices = {}
    
    for feature, domains in data_dict.items():    
        for domain in domains:
            
            # add all data together
            data = data_dict[feature][domain]
            name = feature+'|'+domain
            trans_freq, trans_prop = make_transitions(data)
            
            # save to dicts
            freq_matrices[name] = trans_freq
            prop_matrices[name] = trans_prop            
        
    stacked_freq = pd.DataFrame()
    stacked_prop = pd.DataFrame()
        
    # make the frequency stacked matrices
    for data_name, matrix in freq_matrices.items():
        stacked_freq = stacked_freq.append(matrix)

    # make the proportional stacked matrices
    for data_name, matrix in prop_matrices.items():
        stacked_prop = stacked_prop.append(matrix)
    
    return stacked_freq, stacked_prop