import pandas as pd
import collections

def make_transitions(feature_dict, clause_ends=True):
    '''
    --input--
    feature dictionary
    dict[book] = list(list(strings))
    
    --output--
    x2 df(trans. frequencies x book), df(trans. ratios x book)
    '''
    
    df_Transition_freq = dict() # Transition matrix with frequences
    df_Transition_prob = dict() # Normalized transition matrix

    # a dict to count the transition pairs per book
    transition_pairs = collections.defaultdict(lambda: collections.Counter())
    
    for bookname, clauses in feature_dict.items():
        
        # count transitions using bigrams
        transitions = list()
        for clause in clauses:
            
            if clause_ends:
                transitions.append("Clause_Begin")
                transitions.extend(clause)
                transitions.append("Clause_End")
            else:
                transitions.extend(clause)
            
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
        
        # normalize:
        df_mean = df_trans.sum().mean()
        df_norm = df_trans.apply(lambda col: col * df_mean / col.sum())
        
    return df_trans, df_norm

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