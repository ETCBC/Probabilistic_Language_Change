from tf.fabric import Fabric
import getpass, collections, os

# define books
lbh_books = {'1_Chronicles', '2_Chronicles', 
             'Ezra', 'Esther', 'Nehemiah'}
sbh_books = {'Genesis', 'Exodus','Leviticus', 
             'Deuteronomy','Joshua', 'Judges', 
             '1_Kings', '2_Kings', '1_Samuel',
             '2_Samuel'}


# format paths for Etienne or Cody
etien_path = 'C:/Users/etien/Documents/github/bhsa/tf'
cody_path = '/Users/cody/github/etcbc/bhsa/tf'

if getpass.getuser() == 'etien' and os.path.exists(etien_path):
    locations = etien_path
elif getpass.getuser() == 'cody' and os.path.exists(cody_path):
    locations = cody_path
else:
    raise Exception('Data path is not formatted correctly for Etienne/Cody or data is located elsewhere.')

# load TF and BHSA data
TF = Fabric(locations=locations, modules='c', silent=True)
api = TF.load('''
              otype
              book chapter verse
              function domain
              typ pdp kind
              ''', silent=True)

api.makeAvailableIn(globals()) # globalize TF methods

def get_data(data_path=''):
    
    '''
    This function returns ETCBC BHSA data.
    It loads the data from Text-Fabric.
    '''     
    
    # structure: data[FEATURE][BOOK] = list(list()*N)
    data = collections.defaultdict(lambda: collections.defaultdict(list)) 

    for chapter in F.otype.s('chapter'):

        # format book data
        book, ch, vs = T.sectionFromNode(chapter)
        if book not in (lbh_books | sbh_books): # skip non-studied books
            continue
        book_typ = 'lbh' if book in lbh_books else 'sbh' # set to lbh or sbh

        # text constituents (clause type transitions)
        clauses = L.d(chapter, otype='clause')
        clause_typs = [F.typ.v(clause) for clause in L.d(chapter, otype='clause')]

        # clause constituents
        for clause in clauses:

            # phrase level data
            ph_functions = [F.function.v(phrase) for phrase in L.d(clause, otype='phrase')]
            ph_typs = [F.typ.v(phrase) for phrase in L.d(clause, otype='phrase')]

            # word level data
            parts_of_speech = [F.pdp.v(word) for word in L.d(clause, otype='word')]

            # selection restrictions:
            if any([
                    F.domain.v(clause) != 'N', # must be narrative
                    ]):
                continue # skip it

            # put data in data dict
            data['phrase_functions'][book].append(ph_functions)
            data['phrase_types'][book].append(ph_typs)
            data['word_pos'][book].append(parts_of_speech)

            # add by book type (LBH vs. SBH)
            data['phrase_functions'][book_typ].append(ph_functions)
            data['phrase_types'][book_typ].append(ph_typs)
            data['word_pos'][book_typ].append(parts_of_speech)

        # put data in datadict
        data['clause_types'][book].append(clause_typs)
        data['clause_types'][book_typ].append(clause_typs)
        
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