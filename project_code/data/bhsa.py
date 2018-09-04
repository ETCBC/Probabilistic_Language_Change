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
from tf.extra.bhsa import Bhsa
from data.tree_utils import structure, layout
import getpass, collections, os

# DO PATHS:
etien_path = {'C:/Users/etien/Documents/github/bhsa/tf':'https://github.com/ETCBC/bhsa',
              'C:/Users/etien/Documents/github/lingo/trees/tf':'https://github.com/ETCBC/lingo',
              'C:/Users/etien/Documents/github/parallels/tf':'https://github.com/ETCBC/parallels'}
cody_path = {'/Users/cody/github/etcbc/bhsa/tf':'https://github.com/ETCBC/bhsa',
             '/Users/cody/github/etcbc/lingo/trees/tf':'https://github.com/ETCBC/lingo',
             '/Users/cody/github/etcbc/parallels/tf':'https://github.com/ETCBC/parallels'}
if getpass.getuser() == 'etien':
    locations = etien_path
elif getpass.getuser() == 'cody':
    locations = cody_path
else:
    locations = {}
if not locations:
    raise Exception('Please add your data paths in bhsa.py line 30.')
for path in locations:
    if not os.path.exists(path):
        raise Exception(f'You need an extra datamodule in {os.path.dirname(path)}. Do "git pull {locations[path]}" to this location.')
    
    
# load TF and BHSA data
TF = Fabric(locations=locations.keys(), modules='2017', silent=True)
api = TF.load('''
              otype language
              book chapter verse
              function domain
              typ pdp kind tree
              crossref
              ''', silent=True)

B = Bhsa(api, '', version='2017')

api.makeAvailableIn(globals()) # globalize TF methods

# define book groups & names

lbh_books = ('Song_of_songs', 'Ecclesiastes', 'Esther',
             'Daniel','Ezra', 'Nehemiah', '1_Chronicles', 
             '2_Chronicles')
sbh_books = ('Genesis', 'Exodus','Leviticus', 
             'Deuteronomy','Joshua', 'Judges', 
             '1_Samuel', '2_Samuel', '1_Kings', 
             '2_Kings')
test_books = ('Jonah', 'Ruth')

all_books = tuple(T.sectionFromNode(b)[0] for b in F.otype.s('book')) # use T to get english names

book_sets = {'lbh': lbh_books,
             'sbh': sbh_books,
             'all': all_books}

def filter_parallels(verse_nodes):
    '''
    --input--
    iterable of verse nodes
    
    --output--
    returns list of clause nodes from verses that exhibit 
    <75% similarity with other verses.
    '''
    filtered_clauses = []
    for verse in verse_nodes:
        cr_scores = [cr[1] < 75 for cr in E.crossref.f(verse)]
        if all(cr_scores):
            filtered_clauses.extend(L.d(verse, 'clause'))
    return filtered_clauses

def get_data(books=[]):
    
    '''
    --input--
    books='all'|'sbh'|'lbh'
    or iterable of book names
    
    --output--
    dictionary
        data[feature][domain][book] = list(list(clauses)*N)
    '''     

    # data dictionary containing all data
    # structure: data[FEATURE][BOOK][DOMAIN] = list(list()*N)
    # both narrative and discourse data is gathered
    data = collections.defaultdict(lambda: # feature
                                        collections.defaultdict( # book
                                            lambda: collections.defaultdict(list) # domain
                                        ) 
                                  )
    
    # map Chronicles, Kings, and Samuel to single books
    book_map = {'1_Chronicles': 'Chronicles',
                '2_Chronicles': 'Chronicles',
                '1_Kings': 'Kings',
                '2_Kings': 'Kings',
                '1_Samuel': 'Samuel',
                '2_Samuel': 'Samuel',
                'Ezra': 'Ezra-Nehemiah',
                'Nehemiah': 'Ezra-Nehemiah'}
    
    # configure books list
    if type(books) == str and books in book_sets:
        books = book_sets[books]
    
    elif type(books) == list:
        books_list = tuple()
        for book in books:
            if book in book_sets:
                books_list= books_list + book_sets[book] 
            else:
                books_list = books_list + (book,)
        books = books_list   

    # gather data per group, per book
    for book in books:

        # get node for Text-Fabric processing
        book_node = T.nodeFromSection((book,))
        
        # text constituents (clause type transitions)
        if book in {'1_Chronicles', '2_Chronicles'}:
            clauses = [cl for cl in filter_parallels(L.d(book_node, otype='verse'))]
        else:
            clauses = [cl for cl in filter_parallels(L.d(book_node, otype='verse'))
                          if F.language.v(L.d(cl, 'word')[0]) == 'Hebrew'] # with Hebrew language check
        sentences = [sn for sn in L.d(book_node, otype='sentence')
                        if F.language.v(L.d(sn, 'word')[0]) == 'Hebrew']

        book = book_map.get(book, book) # map Chronicles, Kings, Samuel from individual books
        
        # add clause-level domain (e.g. narrative, quotation); NB fixed from previous version -Cody
        for clause in clauses:
            
            this_domain = F.domain.v(clause)
            this_typ = F.typ.v(clause)
            data['clause_types'][this_domain][book].append([this_typ])
        
        # add phrase- & word-level data to data dict
        for clause in clauses:

            # phrase level data
            ph_functions = [F.function.v(phrase) for phrase in L.d(clause, 'phrase')]
            ph_typs = [F.typ.v(phrase) for phrase in L.d(clause, 'phrase')]

            # word level data
            parts_of_speech = [F.pdp.v(word) for word in L.d(clause, 'word')]
            
            # current domain, i.e. narrative, quotation, etc.
            domain = F.domain.v(clause)
            
            # save clause constituent data
            # put data in data dict
            data['phrase_functions'][domain][book].append(ph_functions)
            data['phrase_types'][domain][book].append(ph_typs)
            data['word_pos'][domain][book].append(parts_of_speech)
                                                                                     
        # add tree data; turned off for now -Cody
#         for sentence in sentences:
#             data['trees'][domain][book].append(structure(F.tree.v(sentence)))

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
    
    