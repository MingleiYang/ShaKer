import numpy as np
from scipy.sparse import vstack
import eden
import eden_rna
from sklearn.ensemble import RandomForestRegressor
import rna_tools

from sklearn.preprocessing import normalize
import xgboost
from scipy.stats import uniform as uni




def crosspredict(data, keys, seq_to_db_function=rna_tools.rnashapes):
    '''
    data = {seqname:[shapearray, sequence, structure]}

    train on n-1 keys, predict on the last,
    yield result for each
    '''
    for key in data.keys():
        print "key ", key
        trainkeys = remove(keys, key)
        mod = make_model(data,trainkeys)
        yield predict(mod, data[key][1], seq_to_db_function=seq_to_db_function)
def remove(li, it):
    '''returns copy of li(st) without "it"'''
    li2 = list(li)
    li2.remove(it)
    return li2






''' old model.. 
RandomForestRegressor(**{'oob_score': False,
                                             'min_impurity_split': 0.01,
                                             'bootstrap': True,
                                             'min_samples_leaf': 1,
                                             'n_estimators': 16,
                                             'min_samples_split': 6,
                                             'min_weight_fraction_leaf': 0.02,
                                             'max_features': None}))
'''
def make_model( data,
                sequence_names=[],
                model= xgboost.XGBRegressor()):
    x,y = getXY(data,sequence_names)
    model.fit(x,y)
    return model

def mask(x,y):
    mask = np.array([ i for i,e in enumerate(y) if e!=None])
    y= np.array(y)
    y=y[mask]
    x=x[mask]
    return x,y


def getXY(data,keys):
    '''takes entries in data that are in the list keys, returns X,Y for regression task'''
    # data is  name -> (react,sequence,dotbacket)
    # we first make some graphs
    react,sequence,stru = zip(*[ data[k] for k in keys ])
    graphs  = map( getgraph, sequence,stru)

    # then we edenize
    x = vstack( eden.graph.vertex_vectorize(graphs,r=3,d=3))
    y= [y for reactlist in react for y in reactlist]
    y= np.array(y)
    # then done
    #print x,y
    return mask(x,y)



def getgraph(sequence,structure):
    """returns networkx graph"""
    return eden_rna.sequence_dotbracket_to_graph(sequence,structure)



def weighted_average(weights, react_arrays):
    '''
    generates l1 norm of weights (sum of absolutes =1)
    then multiplies with the react_arraus,

    t = [np.array(range(3)) for i in range(3)]
    g = [.5] * 3
    d = [t*g for t , g in zip(t,g)]
    print d
    print sum(d)
    '''
    weights = normalize(weights, norm='l1').tolist()[0]
    return sum([ array*weight for array, weight in zip(react_arrays,weights) ])


def predict(model, sequence,seq_to_db_function= rna_tools.rnashapes):
    db_list = seq_to_db_function(sequence)

    if len(db_list)==1:
        graph = eden_rna.sequence_dotbracket_to_graph(seq, stru)
        return model.predict(eg.vertex_vectorize([graph])[0])

    # get probability for each structure
    struct_proba = rna_tools.probabilities_of_structures(sequence, db_list)
    structures, weights =  zip(*struct_proba)

    # edenize and predict reacticuty
    graphs = map(lambda x: getgraph(sequence,x), structures)
    vecs = list(eden.graph.vertex_vectorize(graphs,r=3,d=3))
    predictions_all_structures = [ model.predict(blob) for blob in vecs ]

    # mix reactivity with probabilities
    return weighted_average(weights, predictions_all_structures)



























####
#  CRAP NEEDS COMMENTS
####
def crosspredictInter(data, keys, seq_to_db_function=rna_tools.rnashapes):
    data.pop("R009",None)
    data.pop("23sRNA",None)
    for key in data.keys():
        trainkeys = remove(keys, key)
        mod = make_model(data,trainkeys)
        yield predictInter(mod, data[key][1], seq_to_db_function=seq_to_db_function)

def predictInter(model, sequence,seq_to_db_function= rna_tools.rnashapes):
    struct_proba = rna_tools.probabilities_of_structures(sequence, seq_to_db_function(sequence))# contains one structure and its probability
    structures, weights =  zip(*struct_proba)# one number that specifies the weight
    graphs = map(lambda x: getgraph(sequence,x), structures)
    vecs = list(eden.graph.vertex_vectorize(graphs,r=3,d=3))
    predictions_all_structures = [ model.predict(blob) for blob in vecs ]
    return predictions_all_structures

def modelpredict(data, keys):
    '''
    data = {seqname:[shapearray, sequence, structure]}

    train on n-1 keys, predict on the last,
    yield result for each
    '''
    print "Crosspredict"
    print "keys : ", keys
    #print "data ", data
    trainkeys = ['R009', '23sRNA']
    mod = make_model(data, trainkeys)
    print "trainkeys : ", trainkeys
    for key in data.keys():
        if (key != "R009") and (key != "23sRNA"):
            yield key,predict(mod, data[key][1],lambda x: [data[key][2]])

####
# WHAT IS THIS UNIFORM USED FOR CRAP?
#####
def uniform(lower, upper):
    return uni(lower, upper-lower)










