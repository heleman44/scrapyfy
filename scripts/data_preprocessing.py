import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
import numpy as np
from collections import Counter
from tqdm import tqdm
import meta_data_extraction as meta
import sys
import os
import data_plotting
import utils
import classifier


def Add_country_names(df):
    """
    Add country names to the dataframe. The names can be extracted from the playlist names.
    """
    country_names = [i.split(" - ")[1] for i in list(df.playlist_name)]
    df = df.assign(Country=country_names)
    df.loc[df.Country == "United States", "Country"] = "United States of America"
    df.loc[df.Country == "USA", "Country"] = "United States of America"
    df.loc[df.Country == "Czech Republic", "Country"] = "Czechia"
    df.loc[df.Country == "Dominican Republic", "Country"] = "Dominican Rep."
    return df


def Release_date(df):
    """
    Divide the feature release_date into a simplified verion of release_day, release_month and release_year
    """
    release_date_features = []
    for idx, date in df["release_date"].items():
        try:
            if len(date) == 4:
                year = int(date)
                month = 0
                day = 0

            elif len(date) == 7:
                date_split = date.split("-")
                year, month = int(date_split[0]), int(date_split[1])
                day = 0
            else:
                date_split = date.split("-")
                year, month, day = int(date_split[0]), int(date_split[1]), int(date_split[2])
            release_date_features.append([year, month, day])
        except:
            release_date_features.append([0, 0, 0])

    df["release_year"] = np.array(release_date_features)[:, 0]
    df["release_month"] = np.array(release_date_features)[:, 1]
    df["release_day"] = np.array(release_date_features)[:, 2]
    return df


def filter_countries(df):
    """
    Filter out countries that do not occur in geopandas world
    """
    geopandas_countries = np.sort(gpd.read_file(gpd.datasets.get_path('naturalearth_lowres')).name.to_numpy())
    # with open(f"Data/geopandas_names.txt", "w") as f:
    #     for i in geopandas_countries[:-1]:
    #         f.writelines(i + "\n")
    #     f.writelines(geopandas_countries[-1])
    coutries_list = np.sort(utils.countires_list(df))
    # with open(f"Data/scrapped_country_names.txt", "w") as f:
    #     for i in coutries_list[:-1]:
    #         f.writelines(i + "\n")
    #     f.writelines(coutries_list[-1])
    for c in coutries_list:
        if not c in geopandas_countries and not c == "Global":
            df = df[df.Country != c]
    return df


def filter_playlist_IDs(df):
    df = df[["37i9dQZEVXb" in id for id in df.playlist_id]]
    return df


def df_preparation(df, category, path):
    df = Add_country_names(df)
    df = filter_countries(df)
    df = Release_date(df)
    df.to_csv(f"{path}/{category}_playlists_processed.csv", index=False)
    df = classifier.employ_classifier(df)
    df.to_csv(f"{path}/{category}_playlists_classified.csv", index=False)


def df_preparation_chunked(filename, path, chunksize=10000):
    chunks = pd.read_csv(filename, chunksize=chunksize)
    category_and_path = filename.split("_playlists.csv")[0]
    filename = f'{category_and_path}_playlists_classified.csv'
    if os.path.exists(filename):
        os.remove(filename)
    amount_songs = 0
    for idx, chunk in tqdm(enumerate(chunks), desc="Data preperation"):
        chunk = filter_playlist_IDs(chunk)
        chunk = Add_country_names(chunk)
        # chunk = filter_countries(chunk) #  Singapore, Hong Kong and Global are not in geopandas
        chunk = Release_date(chunk)
        chunk = classifier.employ_classifier(chunk)
        amount_songs += chunk.index.argmax()
        end_date = chunk.scrap_time.tail(1).item()
        if idx == 0:
            start_date = chunk.scrap_time[0]
            counter_c = utils.countires_counter(chunk)
        else:
            counter_c += utils.countires_counter(chunk)
        chunk.to_csv(filename, mode='a', header=not os.path.exists(filename))
    amount_c = len(utils.countires_list(counter=counter_c))
    date = meta.date()
    with open(f"{category_and_path}_meta_data.txt", "w") as f:
        f.writelines([f"{start_date}\n", f"{end_date}\n", f"{amount_songs}\n", f"{amount_c}\n", f"{date}\n"])

def main():

    """
    Read the data csv as a DataFrame
    """
    # name_category = "Viral"
    name_category = "Top"
    path = "Data/06_2023"
    df = pd.read_csv(f"{path}/{name_category}_playlists.csv")

    """
    Filter wrong playlist IDs
    """
    df = filter_playlist_IDs(df)

    """
    Add the country names as a feature
    """
    df = Add_country_names(df)

    """
    Filter out countries that are not in geopandas
    """
    df = filter_countries(df)
   # sys.exit()
    """
    Divide the release date into day, month and year
    """
    df = Release_date(df)

    """
    Plot release features in bar plots
    """
    #data_plotting.plot_release_dates(df, show=True)

    """
    Full preparation chain on full df
    """
    #df_preparation(df, name_category, path)

    """
    Full preparation chain in chunks
    """
    df_preparation_chunked(f"{path}/{name_category}_playlists.csv", path)

if __name__ == "__main__":
    main()