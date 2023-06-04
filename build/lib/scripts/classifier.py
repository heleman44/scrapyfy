import sys
import pandas as pd
import numpy as np
import utils
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
import pickle


def randomforest(X_train, y_train):
    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    return clf


def nn(X_train, y_train):
    clf = MLPClassifier(hidden_layer_sizes=(10, 10, 10), random_state=42, learning_rate='adaptive', max_iter=1000)
    clf = clf.fit(X_train, y_train)
    return clf


def train_model(model="RF"):
    """
    Meta data of the classifier and the trainings data.
    Read the trainings data
    """
    classifier_path = "Classifier"
    name_training_data = "all_tracks_2022_11_12"
    path_training_data = "Data\Training"
    df_training = pd.read_csv(f"{path_training_data}/{name_training_data}.csv")

    """
    Only use happy and sad to train on
    """
    df_training = df_training.drop(df_training[df_training["mood"] == "pride"].index)
    df_training = df_training.drop(df_training[df_training["mood"] == "love"].index)
    df_training = df_training.drop(df_training[df_training["mood"] == "heartbreak"].index)

    """
    Correct typo in trainings data
    """
    df_training.loc[df_training.mood == 'heppy', "mood"] = 'happy'


    keys_for_training = [
        "mood", "acousticness", "danceability",
        "duration_ms", "instrumentalness", "liveness",
        "loudness", "mode", "popularity",
        "speechiness", "tempo", "valence"
        ]

    with open(f"{classifier_path}/keys_for_training.txt", "w") as f:
        for i in keys_for_training[:-1]:
            f.writelines(i + "\n")
        f.writelines(keys_for_training[-1])
    f.close()
    X_train, X_test, y_train, y_test = utils.preprocess_split_dataset_for_training(df_training, keys_for_training, test_size=0, scaler='MinMax')
    if model == "RF":
        classifier_name = "RF"
        classifier = randomforest(X_train, y_train)
    elif model == "nn":
        classifier_name = "nn"
        classifier = nn(X_train, y_train)
    pickle.dump(classifier, open(f"{classifier_path}/{classifier_name}_{name_training_data}.classifier", 'wb'))


def load_model(filename):
    return pickle.load(open(filename, 'rb'))


def employ_classifier(df, filename="Classifier/RF_all_tracks_2022_11_12.classifier"):
    classifier = load_model(filename)
    with open("Classifier/keys_for_training.txt", "r") as f:
        keys_for_training = []
        for i in f:
            keys_for_training.append(i.split("\n")[0])
    min_train, max_train = np.load("Classifier/Scaler_Min_Max.npy", allow_pickle=True)
    X_playlists = (df[keys_for_training[1:]] - min_train) / (max_train - min_train)
    pred_rf_playlists = classifier.predict(X_playlists.values)
    le = preprocessing.LabelEncoder()
    le.classes = np.load('Classifier/LabelEncoder.npy', allow_pickle=True)
    df["mood"] = pred_rf_playlists
    df.loc[df.mood == 0, "mood"] = le.classes[0]
    df.loc[df.mood == 1, "mood"] = le.classes[1]
    return df


def main():
    sys.exit()
    """
    Train a model for classification
    """
    #train_model(model="RF")

    """
    Read the data csv as a DataFrame
    """
    name_category = "Viral"
    path = "Data"
    df = pd.read_csv(f"{path}/{name_category}_playlists_processed.csv")

    """
    Employ the classifier
    """
    df = employ_classifier(df)

    """
    Save classified dataframe
    """
    df.to_csv(f"{path}/{name_category}_playlists_classified.csv", index=False)



if __name__ == "__main__":
    main()