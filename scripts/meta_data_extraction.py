import sys
import pandas as pd
import data_plotting
import utils
import time
import csv


def starting_date(df, show=False):
    start = df["scrap_time"][0]
    if show:
        print(start)
    return start


def latest_scrape(df, show=False):
    latest_scrape = df["scrap_time"].tail(1).item()
    if show:
        print(latest_scrape)
    return latest_scrape


def date(show=False):
    date = time.ctime()
    if show:
        print(date)
    return date


def amount_countires(df=None, counter=None, show=False):
    if counter == None:
        counter = utils.countires_counter(df)
    amount_countires = len(utils.countires_list(counter=counter))
    if show:
        print(amount_countires)
    return amount_countires


def amount_songs(df, show=False):
    df_size = int(df.size / len(df.keys()))
    if show:
        print(df_size)
    return df_size


def meta_data_from_txt():
    filename = "Data/06_2023/meta_data.txt"
    with open(filename, "r") as f:
        meta_data = []
        for i in f:
            meta_data.append(i.split("\n")[0])
    return meta_data


def main():
    """
    Read the data csv as a DataFrame
    """
    name_category = "Viral"
    path = "Data"
    #df = pd.read_csv(f"{path}/{name_category}_playlists_processed.csv")

    #starting_date(df, show=True)
    #amount_countires(df, show=True)
    amount_songs(df, show=True)
    latest_scrape(df, show=True)
    date(show=True)
    sys.exit()

    """
    Divide the release date into day, month and year
    """

    counter_countries = utils.countires_counter(df)
    countires_list = list(counter_countries.keys())

    data_plotting.plot_world_recorded_tracks(df, show=True)


if __name__ == "__main__":
    main()