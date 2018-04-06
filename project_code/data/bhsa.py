'''
This module accesses and returns BHSA data from the Hebrew Bible
which is necessary for analyzing the syntactic transitions in the 
Biblical Hebrew texts. Based on this data, the code found in analysis.py
can build a model of the language tendencies of a given book or group of books.

*IMPORTANT*
If the user is neither Etienne or Cody, they must format their path to their copy
of the BHSA data below or they will receive an error.
'''

from tf.fabric import Fabric
import getpass, collections, os

# format paths for Etienne or Cody
etien_path = 'C:/Users/etien/Documents/github/bhsa/tf'
cody_path = '/Users/cody/github/etcbc/bhsa/tf'

if getpass.getuser() == 'etien' and os.path.exists(etien_path):
    locations = etien_path
elif getpass.getuser() == 'cody' and os.path.exists(cody_path):
    locations = cody_path
else:
    raise Exception('Data path is not formatted correctly...Are you Etienne or Cody? If not, you must change the data path located in project_code/bhsa.py')

# load TF and BHSA data
TF = Fabric(locations=locations, modules='c', silent=True)
api = TF.load('''
              otype
              book chapter verse
              function domain
              typ pdp kind
              ''', silent=True)

api.makeAvailableIn(globals()) # globalize TF methods

# define book groups & names
lbh_books = ('1_Chronicles', '2_Chronicles', 
             'Ezra', 'Esther', 'Nehemiah')
sbh_books = ('Genesis', 'Exodus','Leviticus', 
             'Deuteronomy','Joshua', 'Judges', 
             '1_Kings', '2_Kings', '1_Samuel',
             '2_Samuel')
all_books = tuple(T.sectionFromNode(b)[0] for b in F.otype.s('book')) # use T to get english names

book_sets = {'lbh': lbh_books,
             'sbh': sbh_books,
             'all': all_books}

def get_data(books='all'):
    
    '''
    --input--
    iterable of book names
    
    --output--
    *Data...
    '''     

    # data dictionary containing all data
    # structure: data[FEATURE][BOOK][DOMAIN] = list(list()*N)
    # both narrative and discourse data is gathered
    data = collections.defaultdict(lambda: # feature
                                        collections.defaultdict( # book
                                            lambda: collections.defaultdict(list) # domain
                                        ) 
                                  ) 
    
    # configure books list
    if type(books) == str and books in book_sets:
        books = book_sets[books]
    
    # gather data per group, per book
    for book in books:

        # get node for Text-Fabric processing
        book_node = T.nodeFromSection((book,))

        # text constituents (clause type transitions)
        clauses = L.d(book_node, otype='clause')

        # add clause-level data to data dict
        for this_domain in ('N', 'D'): # narrative/discourse
            clause_typs = [F.typ.v(clause) for clause in L.d(book_node, otype='clause') # cl types by domain
                              if F.domain.v(clause) == this_domain]
            data['clause_types'][book][this_domain].append(clause_typs)
        
        # add phrase- & word-level data to data dict
        for clause in clauses:

            # phrase level data
            ph_functions = [F.function.v(phrase) for phrase in L.d(clause, otype='phrase')]
            ph_typs = [F.typ.v(phrase) for phrase in L.d(clause, otype='phrase')]

            # word level data
            parts_of_speech = [F.pdp.v(word) for word in L.d(clause, otype='word')]
            
            # current domain, i.e. narrative or discourse
            domain = F.domain.v(clause)
            
            # save clause constituent data
            # put data in data dict
            data['phrase_functions'][book][domain].append(ph_functions)
            data['phrase_types'][book][domain].append(ph_typs)
            data['word_pos'][book][domain].append(parts_of_speech)
            
    # return all data
    return data

def unique(otype='', feature=''):
    '''
    Returns sorted list of unique features from BHSA data.
    Sort by the frequency of the feature, most frequent first.
    '''
    
    if not otype:
        raise Exception('otype not provided! Give an object type (e.g. otype="phrase")')
    elif not feature:
        raise Exception('feature not provided! Give a feature (e.g. feature="function")')
 
    feature = eval(f'F.{feature}')

    feature_count = collections.Counter()
    
    for obj in F.otype.s(otype):
        feature_count[feature.v(obj)] += 1
    
    unique_features = list(v[0] for v in feature_count.most_common())
    
    return unique_features
