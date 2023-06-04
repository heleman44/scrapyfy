import sys
import os
import pandas as pd
import numpy as np
from collections import Counter
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report

def countires_counter(df):
    """
    Get a the counter of all the countries for which data is available
    """
    counter_countries = Counter(df.Country)
    return counter_countries


def countires_list(df=None, counter=None, show=False):
    """
    Get a list of all the countries for which data is available
    """
    if counter == None:
        counter = countires_counter(df)
    list_countires = list(counter.keys())
    return list_countires


def preprocess_split_dataset_for_training(df, keys_for_traning, test_size=0.2, scaler='MinMax'):
    """
    Preprocess and split a statify dataset data frame to a training and a test set.
    The mood column of the data frame is encoded and the other keys of interest are scaled
    by a MinMax or a Standard scaler. The performance of a neural net should thereby enhance.

    Parameters
    ----------
    df : pandas.DataFrame
        Typical statify data frame, which contains all information about the songs.
    keys_for_traning : list[str]
        List of the df's key names that are relevant to train a neural net.
    test_size : float, optional
        This parameter adjusts the test datasets size relative to the training dataset.
        This values can not exceed 1.

    Returns
    -------
    X_train : pandas.DataFrame
        Features of the train dataset.
    X_test : pandas.DataFrame
        Features of the test dataset.
    y_train : pandas.DataFrame
        Labels of the train dataset.
    y_test : pandas.DataFrame
        Labels of the test dataset.
    """
    df_doi = df[keys_for_traning]  # Only use the relevant columns of df
    moods = df_doi['mood']
    le = preprocessing.LabelEncoder()
    le.fit(moods)
    y = le.transform(moods)
    np.save('Classifier/LabelEncoder.npy',
            le.classes_)  # https://stackoverflow.com/questions/28656736/using-scikits-labelencoder-correctly-across-multiple-programs

    X = df_doi.drop(['mood'], axis=1)
    if test_size:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    else:
        X_train, X_test, y_train, y_test = X, 0, y, 0

    # Scale test and training dataset separately, to avoid that the datasets influence each other (See doumentation
    # sklearn.preprocessing.scale)
    if scaler == 'MinMax':
        scaler = preprocessing.MinMaxScaler()  # scales: (x - x_min) / (x_max - x_min)
        X_train_scaler = scaler.fit(X_train)
        min_train, max_train = X_train_scaler.data_min_, X_train_scaler.data_max_
        np.save('Classifier/Scaler_Min_Max.npy', [min_train, max_train])
        if test_size:
            X_test = (X_test.to_numpy() - min_train) / (max_train - min_train)
    elif scaler == 'Standard':
        scaler = preprocessing.StandardScaler()  # scales: (x - mean) / std
        X_train_scaler = scaler.fit(X_train)
        mean_train, std_train = X_train_scaler.mean_, X_train_scaler.var_
        np.save('Classifier/Scaler_Mean_Std.npy', [mean_train, std_train])
        if test_size:
            X_test = scaler.fit_transform(X_test, with_mean=mean_train, with_std=std_train)
    else:
        sys.exit(f'\nScaler {scaler} not known\nPossible scalers are \'MinMax\' and \'Standard\'')

    X_train = X_train_scaler.transform(X_train)

    return X_train, X_test, y_train, y_test


def valid_country(chunks, country):
    for chunk in chunks:
        mask = [c in country for c in chunk["Country"]]
        yield chunk.loc[mask]


def read_country_df(filename, country, chunksize=10000):
    chunks = pd.read_csv(filename, chunksize=chunksize)
    if type(country) == str:
        country = [country]
    df = pd.concat(valid_country(chunks, country))
    return df


def countries_mood_chunk(chunks):
    for chunk in chunks:
        yield chunk.loc[:, ["mood", "Country"]]


def read_countries_mood_df(filename, chunksize=10000):
    chunks = pd.read_csv(filename, chunksize=chunksize)
    df = pd.concat(countries_mood_chunk(chunks))
    return df