import matplotlib.pyplot as plt
import matplotlib.dates as md
import datetime as dt
import time
import sys
import geopandas as gpd
import pandas as pd
import numpy as np
import utils
from matplotlib import rcParams
color = ["k", "r", "g", "b", "m", "sienna", "c", "tab:orange", "tab:pink", "gold"]
# rcParams['axes.prop_cycle'] = mpl.cycler(color=color)

def plot_release_dates(df, show=False):
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    ax1.hist(df["release_day"].to_numpy(), density=True, bins=np.linspace(-0.5, 31.5, 32))
    ax1.set_xlabel("Day")
    ax1.set_ylabel("Propability [%]")
    ax1.set_xticks(np.linspace(0, 30, 7), ["None", 5, 10, 15, 20, 25, 30])
    ax2.set_title("Release month")
    ax2.hist(df["release_month"], density=True, bins=np.linspace(-0.5, 12.5, 13))
    ax2.set_xlabel("Month")
    ax2.set_xticks(np.linspace(0, 12, 7), ["None", 2, 4, 6, 8, 10, 12])
    ax2.set_ylabel("Propability [%]")
    ax3.set_title("Release year")
    ax3.hist(df["release_year"], density=True, bins=df["release_year"].max() - df["release_year"].min())
    ax3.set_xlabel("Year")
    ax3.set_ylabel("Propability [%]")
    ax3.set_xlim(df.release_year.drop(df[df.release_date == "0000"].index.to_numpy()).min(), df.release_year.max())
    if show:
        plt.show()
    else:
        return fig


def plot_world_recorded_tracks(df, show=False):
    counter_countries = utils.countires_counter(df)
    countires_list = list(counter_countries.keys())


    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    recorded = []
    for c in world.name:
        if c in countires_list:
            idx_c = countires_list.index(c)
            recorded.append(list(counter_countries.values())[idx_c])
        else:
            recorded.append(None)

    world["recorded"] = recorded
    map_ax = world.plot(column="recorded", legend=True, legend_kwds={'label': "Recorded tracks",'orientation': "horizontal"}, figsize=(10,6),
    missing_kwds={
        "color": "lightgrey",
        #"edgecolor": "red",
        #"hatch": "///",
        "label": "Missing values",
    },);
    if show:
        plt.show()
    else:
        return map_ax


def plot_recorded_for_list_of_countries(df, list_countries, show=False):
    countries = utils.countires_list(df)
    if type(list_countries) == str:
        list_countries = [list_countries]
    recorded = []
    dates_list = []
    found_c = []
    for c in list_countries:
        if not c in countries:
            continue
        found_c.append(c)
        df_c = df[df.Country == c]
        timestamps = df_c.scrap_time_unix
        dates = [dt.datetime.fromtimestamp(ts) for ts in timestamps]
        #plt.plot(dates, label=c)
        """
        Get data binned for the dates
        """
        hist, bin_edges, patches = plt.hist(dates, alpha=0.75, label=c)
        """
        Calculate the ratio of happy to total
        """
        x_values = (bin_edges[:-1] + bin_edges[1:]) / 2
        dates_list.append(x_values)
        recorded.append(hist)
    plt.clf()
    fig = plt.figure()
    plt.subplots_adjust(bottom=0.2)
    plt.xticks(rotation=25)
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(xfmt)
    for (c, d, r) in zip(found_c, dates_list, recorded):
        plt.plot(d, r, "o--", label=c)
    plt.ylabel("Recorded tracks")
    plt.legend()
    plt.grid()
    if show:
        plt.show()
    else:
        return fig

    
def plot_world_ratio_happy(df, show=False):
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    ratio_happy = []
    for c in world.name:
        if c in utils.countires_list(df):
            df_c = df[df.Country == c]
            happy = df_c[df_c.mood == "happy"].size
            total = df_c.size
            ratio_happy.append(happy / total)
        else:
            ratio_happy.append(None)

    world["ratio_happy"] = ratio_happy
    map_ax = world.plot(column="ratio_happy", legend=True, legend_kwds={'label': "Ratio of happy songs ",'orientation': "horizontal"}, figsize=(10,6),
    missing_kwds={
        "color": "lightgrey",
        #"edgecolor": "red",
        #"hatch": "///",
        "label": "Missing values",
    },)
    if show:
        plt.show()
    else:
        return map_ax


def plot_world_ratio_sad(df, show=False):
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    ratio_sad = []
    for c in world.name:
        if c in utils.countires_list(df):
            df_c = df[df.Country == c]
            sad = df_c[df_c.mood == "sad"].size
            total = df_c.size
            ratio_sad.append(sad / total)
        else:
            ratio_sad.append(None)

    world["ratio_sad"] = ratio_sad
    map_ax = world.plot(column="ratio_sad", legend=True, legend_kwds={'label': "Ratio of sad songs ",'orientation': "horizontal"}, figsize=(10,6),
    missing_kwds={
        "color": "lightgrey",
        #"edgecolor": "red",
        #"hatch": "///",
        "label": "Missing values",
    },)
    if show:
        plt.show()
    else:
        return map_ax


def plot_mood_for_single_country(df, country, show=False):
    df_c = df[df.Country == country]
    timestamps_happy, timestamps_sad = df_c[df_c.mood == "happy"].scrap_time_unix, df_c[df_c.mood == "sad"].scrap_time_unix
    dates_happy, dates_sad = [dt.datetime.fromtimestamp(ts) for ts in timestamps_happy], [dt.datetime.fromtimestamp(ts) for ts in timestamps_sad]
    """
    Get happy and sad data binned for the dates
    """
    hist_happy, bin_edges_happy, patches_happy = plt.hist(dates_happy)
    hist_sad, bin_edges_sad, patches_sad = plt.hist(dates_sad, bins=bin_edges_happy)
    plt.clf()
    """
    Calculate the ratio of happy to total
    """
    fig = plt.figure()
    plt.subplots_adjust(bottom=0.2)
    plt.xticks(rotation=25)
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(xfmt)
    x_values = (bin_edges_happy[:-1] + bin_edges_happy[1:]) / 2
    plt.plot(x_values, hist_happy / (hist_happy + hist_sad), "ok--", label=country)
    plt.ylabel("Ratio of happy songs")
    plt.legend()
    plt.grid()
    if show:
        plt.show()
    else:
        return fig

    
def plot_mood_for_list_of_countries(df, list_countries, show=False):
    countries = utils.countires_list(df)
    happy_ratio = []
    dates = []
    found_c = []
    for c in list_countries:
        if not c in countries:
            continue
        found_c.append(c)
        df_c = df[df.Country == c]
        timestamps_happy, timestamps_sad = df_c[df_c.mood == "happy"].scrap_time_unix, df_c[df_c.mood == "sad"].scrap_time_unix
        dates_happy, dates_sad = [dt.datetime.fromtimestamp(ts) for ts in timestamps_happy], [dt.datetime.fromtimestamp(ts) for ts in timestamps_sad]
        """
        Get happy and sad data binned for the dates
        """
        hist_happy, bin_edges_happy, patches_happy = plt.hist(dates_happy)
        hist_sad, bin_edges_sad, patches_sad = plt.hist(dates_sad, bins=bin_edges_happy)
        """
        Calculate the ratio of happy to total
        """
        x_values = (bin_edges_happy[:-1] + bin_edges_happy[1:]) / 2
        dates.append(x_values)
        happy_ratio.append(hist_happy / (hist_happy + hist_sad))
    plt.clf()
    fig = plt.figure()
    plt.subplots_adjust(bottom=0.2)
    plt.xticks(rotation=25)
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(xfmt)
    for (c, d, hr) in zip(found_c, dates, happy_ratio):
        plt.plot(d, hr, "o--", label=c)
    plt.ylabel("Ratio of happy songs")
    plt.legend()
    plt.grid()
    if show:
        plt.show()
    else:
        return fig


def main():
    """
    Read the data csv as a DataFrame
    """
    name_category = "Viral"
    path = "Data"
    #df = pd.read_csv(f"{path}/{name_category}_playlists_classified.csv")

    # plot_world_recorded_tracks(df, show=True)

    #fig = plot_mood_for_single_country(df, "Czechia")

    #plot_world_ratio_happy(df, show=True)
    #plot_world_ratio_sad(df, show=True)

    countries_of_interest = ["Germany", "France", "United Kingdom", "United States of America", "Ukraine", "Japan", "India", "Saudi Arabia"]
    df_c = utils.read_country_df(f"{path}/{name_category}_playlists_classified.csv", countries_of_interest) 
    print(df_c[df_c.Country == "United States of America"].scrap_time.tail())
    sys.exit()
    fig = plot_recorded_for_list_of_countries(df_c, countries_of_interest, show=True)
    #fig.savefig("test.png")

    df = utils.read_countries_mood_df(f"{path}/{name_category}_playlists_classified.csv")
    fig = plot_world_ratio_happy(df)
    fig.savefig("static/plot.png")


if __name__ == "__main__":
    main()