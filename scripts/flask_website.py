from flask import Flask, render_template, request
import pandas as pd
import data_preprocessing
import data_plotting
import utils
import meta_data_extraction as meta
import matplotlib.pyplot as plt
import threading
from pyngrok import ngrok
plt.switch_backend('agg')

global category
category = "Viral"

def get_token():
    token_file = 'token.txt'

    with open(token_file,'r') as f:
        token=f.read()
    token=token.split()[0]
    return token

app = Flask(__name__)

@app.route("/")
def index():
    global category
    meta_data = meta.meta_data_from_txt()
    starting_date = meta_data[0]
    latest_scrape = meta_data[1]
    amount_s = meta_data[2]
    amount_c = meta_data[3]
    date = meta_data[4]
    return render_template("home.html", date=date, start=starting_date, last=latest_scrape, countires=amount_c, songs=amount_s, category=category)


@app.route("/png")
def png():
    return render_template("image.html")


@app.route("/change_categroy", methods=["POST"])
def change_categroy():
    global category
    if category == "Viral":
        category = "Top"
    else:
        category = "Viral"
    return render_template("change_category.html", category=category)


@app.route("/data_preparation", methods=["POST"])
def data_preparation():
    data_preprocessing.df_preparation_chunked(f"Data/06_2023/{category}_playlists.csv")
    return render_template("preprocessed.html")

@app.route("/c_hr", methods=["POST"])
def c_hr():
    user_input = request.form["user_input"]
    try:
        df = utils.read_country_df(f"Data/06_2023/{category}_playlists_classified.csv", user_input)
        fig = data_plotting.plot_mood_for_single_country(df, user_input)
        fig.savefig("static/plot.png")
        return render_template("image.html")
    except Exception as e:
        return f"You entered: {user_input}, which is no possible input.\nPossible input: {utils.countires_list(df)}"


@app.route("/png_list_c_hr", methods=["POST"])
def png_list_c_hr():
    countries_of_interest = ["Global", "Germany", "France", "United Kingdom", "United States of America", "Ukraine", "Japan", "India", "Saudi Arabia", "South Africa"]
    df = utils.read_country_df(f"Data/06_2023/{category}_playlists_classified.csv", countries_of_interest)
    fig = data_plotting.plot_mood_for_list_of_countries(df, countries_of_interest)
    fig.savefig("static/plot.png")
    return render_template("image.html")


@app.route("/png_list_c_r", methods=["POST"])
def png_list_c_r():
    countries_of_interest = ["Global", "Germany", "France", "United Kingdom", "United States of America", "Ukraine", "Japan", "India", "Saudi Arabia", "South Africa"]
    df = utils.read_country_df(f"Data/06_2023/{category}_playlists_classified.csv", countries_of_interest)
    fig = data_plotting.plot_recorded_for_list_of_countries(df, countries_of_interest)
    fig.savefig("static/plot.png")
    return render_template("image.html")

@app.route("/c_r", methods=["POST"])
def c_r():
    user_input = request.form["user_input"]
    try:
        df = utils.read_country_df(f"Data/06_2023/{category}_playlists_classified.csv", user_input)
        fig = data_plotting.plot_recorded_for_list_of_countries(df, user_input)
        fig.savefig("static/plot.png")
        return render_template("image.html")
    except Exception as e:
        return f"You entered: {user_input}, which is no possible input.\nPossible input: {utils.countires_list(df)}"

@app.route("/png_world_ratio", methods=["POST"])
def png_world_ratio():
    df = utils.read_countries_mood_df(f"Data/06_2023/{category}_playlists_classified.csv")
    plt.clf()
    fig = data_plotting.plot_world_ratio_happy(df)
    plt.savefig("static/plot.png")
    return render_template("image.html")

@app.route("/png_world_recorded", methods=["POST"])
def png_world_recorded():
    df = utils.read_countries_mood_df(f"Data/06_2023/{category}_playlists_classified.csv")
    plt.clf()
    fig = data_plotting.plot_world_recorded_tracks(df)
    plt.savefig("static/plot.png")
    return render_template("image.html")

def run_app():
    app.run(port=5000)# ssl_context='adhoc', host='0.0.0.0', port=5000)



if __name__ == "__main__":
    app_thread = threading.Thread(target=run_app)
    app_thread.start()
    token=get_token()
    ngrok.set_auth_token(token)

    # Create a tunnel to the Flask app and expose it using ngrok
    public_url = ngrok.connect(5000)
    print(f"Your Flask app is accessible at: {public_url}")

