import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers.core import Dropout, Activation, Dense
from keras.layers.normalization import BatchNormalization
from keras.layers.advanced_activations import PReLU
from keras.utils import np_utils
from sklearn.metrics import log_loss
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
import datetime

## settings
dataset_version = "lvl2MP"
model_type = "keras"
seed_value = 1543
todate = datetime.datetime.now().strftime("%Y%m%d")
np.random.seed(seed_value)
np.random.seed(22432)  # for reproducibility
need_normalise=True
need_categorical=False

def getDummy(df,col):
    category_values=df[col].unique()
    data=[[0 for i in range(len(category_values))] for i in range(len(df))]
    dic_category=dict()
    for i,val in enumerate(list(category_values)):
        dic_category[str(val)]=i
   # print dic_category
    for i in range(len(df)):
        data[i][dic_category[str(df[col][i])]]=1

    data=np.array(data)
    for i,val in enumerate(list(category_values)):
        df.loc[:,"_".join([col,str(val)])]=data[:,i]

    return df

train = pd.read_csv('../input2/xtrain_'+ dataset_version + '.csv')
id_train = train.ID
y_train_target = train.target
y_train = train.target
train.drop('ID', axis = 1, inplace = True)
train.drop('target', axis = 1, inplace = True)

test = pd.read_csv('../input2/xtest_'+ dataset_version + '.csv')
id_test = test.ID
test.drop('ID', axis = 1, inplace = True)

encoder = LabelEncoder()
y_train = encoder.fit_transform(y_train).astype(np.int32)
y_train = np_utils.to_categorical(y_train)

print ("processsing finished")
train = np.array(train)
train = train.astype(np.float32)
test = np.array(test)
test = test.astype(np.float32)
if need_normalise:
    scaler = StandardScaler().fit(train)
    train = scaler.transform(train)
    test = scaler.transform(test)

# folds
xfolds = pd.read_csv('../input/xfolds.csv')
# work with 5-fold split
fold_index = xfolds.fold5
fold_index = np.array(fold_index) - 1
n_folds = len(np.unique(fold_index))

nb_classes = 2
print nb_classes, 'classes'

dims = train.shape[1]
print dims, 'dims'

auc_scores=[]
best_score=-1

param_grid = [[int(0.5 * train.shape[1]), 0.05, int(0.25 * train.shape[1]), 0.025, 40, 2256],
              [int(0.9 * train.shape[1]), 0.05, int(0.45 * train.shape[1]), 0.025, 40, 2256],
              [int(1.2 * train.shape[1]), 0.05, int(0.6 * train.shape[1]), 0.025, 40, 2256],
              [int(0.5 * train.shape[1]), 0.1, int(0.25 * train.shape[1]), 0.05, 40, 2256],
              [int(0.9 * train.shape[1]), 0.1, int(0.45 * train.shape[1]), 0.05, 40, 2256],
              [int(1.2 * train.shape[1]), 0.1, int(0.6 * train.shape[1]), 0.05, 40, 2256],
              [int(0.5 * train.shape[1]), 0.2, int(0.25 * train.shape[1]), 0.1, 40, 2256],
              [int(0.9 * train.shape[1]), 0.2, int(0.45 * train.shape[1]), 0.1, 40, 2256],
              [int(1.2 * train.shape[1]), 0.2, int(0.6 * train.shape[1]), 0.1, 40, 2256],
              [int(0.5 * train.shape[1]), 0.25, int(0.25 * train.shape[1]), 0.125, 40, 2256],
              [int(0.9 * train.shape[1]), 0.25, int(0.45 * train.shape[1]), 0.125, 40, 2256],
              [int(1.2 * train.shape[1]), 0.25, int(0.6 * train.shape[1]), 0.125, 40, 2256],
              [int(0.5 * train.shape[1]), 0.4, int(0.25 * train.shape[1]), 0.2, 40, 2256],
              [int(0.9 * train.shape[1]), 0.4, int(0.45 * train.shape[1]), 0.2, 40, 2256],
              [int(1.2 * train.shape[1]), 0.4, int(0.6 * train.shape[1]), 0.2, 40, 2256],
              [int(0.5 * train.shape[1]), 0.05, int(0.25 * train.shape[1]), 0.025, 20, 2256],
              [int(0.9 * train.shape[1]), 0.05, int(0.45 * train.shape[1]), 0.025, 20, 2256],
              [int(1.2 * train.shape[1]), 0.05, int(0.6 * train.shape[1]), 0.025, 20, 2256],
              [int(0.5 * train.shape[1]), 0.1, int(0.25 * train.shape[1]), 0.05, 20, 2256],
              [int(0.9 * train.shape[1]), 0.1, int(0.45 * train.shape[1]), 0.05, 20, 2256],
              [int(1.2 * train.shape[1]), 0.1, int(0.6 * train.shape[1]), 0.05, 20, 2256],
              [int(0.5 * train.shape[1]), 0.2, int(0.25 * train.shape[1]), 0.1, 20, 2256],
              [int(0.9 * train.shape[1]), 0.2, int(0.45 * train.shape[1]), 0.1, 20, 2256],
              [int(1.2 * train.shape[1]), 0.2, int(0.6 * train.shape[1]), 0.1, 20, 2256],
              [int(0.5 * train.shape[1]), 0.25, int(0.25 * train.shape[1]), 0.125, 20, 2256],
              [int(0.9 * train.shape[1]), 0.25, int(0.45 * train.shape[1]), 0.125, 20, 2256],
              [int(1.2 * train.shape[1]), 0.25, int(0.6 * train.shape[1]), 0.125, 20, 2256],
              [int(0.5 * train.shape[1]), 0.4, int(0.25 * train.shape[1]), 0.2, 20, 2256],
              [int(0.9 * train.shape[1]), 0.4, int(0.45 * train.shape[1]), 0.2, 20, 2256],
              [int(1.2 * train.shape[1]), 0.4, int(0.6 * train.shape[1]), 0.2, 20, 2256],
               
              [int(0.5 * train.shape[1]), 0.05, int(0.25 * train.shape[1]), 0.025, 40, 10000],
              [int(0.9 * train.shape[1]), 0.05, int(0.45 * train.shape[1]), 0.025, 40, 10000],
              [int(1.2 * train.shape[1]), 0.05, int(0.6 * train.shape[1]), 0.025, 40, 10000],
              [int(0.5 * train.shape[1]), 0.1, int(0.25 * train.shape[1]), 0.05, 40, 10000],
              [int(0.9 * train.shape[1]), 0.1, int(0.45 * train.shape[1]), 0.05, 40, 10000],
              [int(1.2 * train.shape[1]), 0.1, int(0.6 * train.shape[1]), 0.05, 40, 10000],
              [int(0.5 * train.shape[1]), 0.2, int(0.25 * train.shape[1]), 0.1, 40, 10000],
              [int(0.9 * train.shape[1]), 0.2, int(0.45 * train.shape[1]), 0.1, 40, 10000],
              [int(1.2 * train.shape[1]), 0.2, int(0.6 * train.shape[1]), 0.1, 40, 10000],
              [int(0.5 * train.shape[1]), 0.25, int(0.25 * train.shape[1]), 0.125, 40, 10000],
              [int(0.9 * train.shape[1]), 0.25, int(0.45 * train.shape[1]), 0.125, 40, 10000],
              [int(1.2 * train.shape[1]), 0.25, int(0.6 * train.shape[1]), 0.125, 40, 10000],
              [int(0.5 * train.shape[1]), 0.4, int(0.25 * train.shape[1]), 0.2, 40, 10000],
              [int(0.9 * train.shape[1]), 0.4, int(0.45 * train.shape[1]), 0.2, 40, 10000],
              [int(1.2 * train.shape[1]), 0.4, int(0.6 * train.shape[1]), 0.2, 40, 10000],
              [int(0.5 * train.shape[1]), 0.05, int(0.25 * train.shape[1]), 0.025, 20, 10000],
              [int(0.9 * train.shape[1]), 0.05, int(0.45 * train.shape[1]), 0.025, 20, 10000],
              [int(1.2 * train.shape[1]), 0.05, int(0.6 * train.shape[1]), 0.025, 20, 10000],
              [int(0.5 * train.shape[1]), 0.1, int(0.25 * train.shape[1]), 0.05, 20, 10000],
              [int(0.9 * train.shape[1]), 0.1, int(0.45 * train.shape[1]), 0.05, 20, 10000],
              [int(1.2 * train.shape[1]), 0.1, int(0.6 * train.shape[1]), 0.05, 20, 10000],
              [int(0.5 * train.shape[1]), 0.2, int(0.25 * train.shape[1]), 0.1, 20, 10000],
              [int(0.9 * train.shape[1]), 0.2, int(0.45 * train.shape[1]), 0.1, 20, 10000],
              [int(1.2 * train.shape[1]), 0.2, int(0.6 * train.shape[1]), 0.1, 20, 10000],
              [int(0.5 * train.shape[1]), 0.25, int(0.25 * train.shape[1]), 0.125, 20, 10000],
              [int(0.9 * train.shape[1]), 0.25, int(0.45 * train.shape[1]), 0.125, 20, 10000],
              [int(1.2 * train.shape[1]), 0.25, int(0.6 * train.shape[1]), 0.125, 20, 10000],
              [int(0.5 * train.shape[1]), 0.4, int(0.25 * train.shape[1]), 0.2, 20, 10000],
              [int(0.9 * train.shape[1]), 0.4, int(0.45 * train.shape[1]), 0.2, 20, 10000],
              [int(1.2 * train.shape[1]), 0.4, int(0.6 * train.shape[1]), 0.2, 20, 10000],

              [int(1.9 * train.shape[1]), 0.1, int(1.45 * train.shape[1]), 0.05, 40, 10000],
              [int(2.2 * train.shape[1]), 0.1, int(1.6 * train.shape[1]), 0.05, 40, 10000],
              [int(4.5 * train.shape[1]), 0.2, int(1.25 * train.shape[1]), 0.1, 40, 10000],
              [int(1.9 * train.shape[1]), 0.2, int(1.45 * train.shape[1]), 0.1, 60, 10000],
              [int(2.2 * train.shape[1]), 0.2, int(1.6 * train.shape[1]), 0.1, 60, 10000],
              [int(4.5 * train.shape[1]), 0.25,int(1.25 * train.shape[1]), 0.125, 60, 10000],
              [int(1.9 * train.shape[1]), 0.25,int(1.45 * train.shape[1]), 0.125, 120, 10000],
              [int(2.2 * train.shape[1]), 0.25,int(1.6 * train.shape[1]), 0.125, 120, 10000],
              [int(4.5 * train.shape[1]), 0.4, int(1.25 * train.shape[1]), 0.2, 120, 10000],
              [int(1.9 * train.shape[1]), 0.4, int(1.45 * train.shape[1]), 0.2, 240, 10000],
              [int(1.2 * train.shape[1]), 0.4, int(1.6 * train.shape[1]), 0.2, 240, 10000]

              ]

# storage structure for forecasts
mvalid = np.zeros((train.shape[0],len(param_grid)))
mfull = np.zeros((test.shape[0],len(param_grid)))

## build 2nd level forecasts
for i in range(len(param_grid)):
        print "processing parameter combo:", param_grid[i]
        print "Combo:", i+1, "of", len(param_grid)
        # loop over folds
        # Recompile model on each fold
        for j in range(0,n_folds):
            # configure model with j-th combo of parameters
            x = param_grid[i]
            model = Sequential()
            model.add(Dense(x[0], input_shape=(dims,)))
            model.add(Dropout(x[1]))# input dropout
            #model.add(PReLU())
            # model.add(BatchNormalization())
            model.add(Dense(x[2]))
            #model.add(PReLU())
            model.add(BatchNormalization())
            model.add(Dropout(x[3]))
            model.add(Dense(nb_classes))
            model.add(Activation('softmax'))
            model.compile(loss='binary_crossentropy', optimizer="adadelta")

            idx0 = np.where(fold_index != j)
            idx1 = np.where(fold_index == j)
            x0 = np.array(train)[idx0,:][0]
            x1 = np.array(train)[idx1,:][0]
            y0 = np.array(y_train)[idx0]
            y1 = np.array(y_train)[idx1]

            model.fit(x0, y0, nb_epoch=x[4], batch_size=x[5])
            mvalid[idx1,i] = model.predict_proba(x1)[:,1]
            y_pre = model.predict_proba(x1)[:,1]
            scores = log_loss(y1[:,1],y_pre)
            print 'LogLoss score', scores
            del model
            print "finished fold:", j

        print "Building full prediction model for test set."
        # configure model with j-th combo of parameters
        x = param_grid[i]
        model = Sequential()
        model.add(Dense(x[0], input_shape=(dims,)))
        model.add(Dropout(x[1]))# input dropout
        #model.add(PReLU())
        # model.add(BatchNormalization())
        model.add(Dense(x[2]))
        #model.add(PReLU())
        model.add(BatchNormalization())
        model.add(Dropout(x[3]))
        model.add(Dense(nb_classes))
        model.add(Activation('softmax'))
        model.compile(loss='binary_crossentropy', optimizer="adadelta")
        # fit on complete dataset

        model.fit(np.array(train), y_train, nb_epoch=x[4], batch_size=x[5])
        mfull[:,i] = model.predict_proba(np.array(test))[:,1]

        del model
        print "finished full prediction"
build_meta_keras2.py
## store the results
# add indices etc
mvalid = pd.DataFrame(mvalid)
mvalid.columns = [model_type + str(i) for i in range(0, mvalid.shape[1])]
mvalid['ID'] = id_train
mvalid['target'] = y_train_target

mfull = pd.DataFrame(mfull)
mfull.columns = [model_type + str(i) for i in range(0, mfull.shape[1])]
mfull['ID'] = id_test


# save the files
mvalid.to_csv('../metafeatures2/prval_' + model_type + '_' + todate + '_data' + dataset_version + '_seed' + str(seed_value) + '.csv', index = False, header = True)
mfull.to_csv('../metafeatures2/prfull_' + model_type + '_' + todate + '_data' + dataset_version + '_seed' + str(seed_value) + '.csv', index = False, header = True)
