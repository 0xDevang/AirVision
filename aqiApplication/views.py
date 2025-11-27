import os
from django.conf import settings
from django.http import HttpResponse
#from .models import City
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import requests
from django.shortcuts import render
import seaborn as sns

TOKEN = "da6c119a584bd1a00de09214930f21a23900a9a5"

CITIES = ["Delhi", "Mumbai", "Ahmedabad", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune","Jaipur"]

DEFAULT_CITY = "Delhi"

def fetch_city_data(city):
    url = f"https://api.waqi.info/feed/{city}/?token={TOKEN}"
    response = requests.get(url).json()

    if response["status"] == "ok":
        data = response["data"]

        pollutants = data.get("iaqi", {})  # pollutant concentrations

        return {
            "city": city,
            "aqi": data.get("aqi", "N/A"),
            "dominant_pollutant": data.get("dominentpol", "N/A"),
            "time": data["time"]["s"],

            # Pollutant concentrations
            "pm25": pollutants.get("pm25", {}).get("v", None),
            "pm10": pollutants.get("pm10", {}).get("v", None),
            "o3": pollutants.get("o3", {}).get("v", None),
            "no2": pollutants.get("no2", {}).get("v", None),
            "so2": pollutants.get("so2", {}).get("v", None),
            "co": pollutants.get("co", {}).get("v", None),

            # Metadata
            "station": data.get("city", {}).get("name", "N/A"),
            "geo": data.get("city", {}).get("geo", []),
        }

    return None

def home(request):
    #city = request.GET.get("search", DEFAULT_CITY)
    city = request.GET.get("city", DEFAULT_CITY)
    result = fetch_city_data(city)
    if not result :
        return render(request, "Error.html")

    pollutants = [
        ("PM2.5", result["pm25"]),
        ("PM10", result["pm10"]),
        ("Ozone (O₃)", result["o3"]),
        ("NO₂", result["no2"]),
        ("SO₂", result["so2"]),
        ("CO", result["co"]),
    ]

    return render(request, "aqiApplication/home.html", {
        "result": result,
        "pollutants": pollutants
    })

def allCities(request):
    results = [fetch_city_data(city) for city in CITIES]
    return render(request, "aqiApplication/allCities.html", {"results": results})



def about(request):
    return render(request, "aqiApplication/about.html")




# ============ air_app ===========
def analysis(request):

    charts_dir = os.path.join(settings.BASE_DIR, "static", "charts")
    os.makedirs(charts_dir, exist_ok=True)

    # ------------------ 1. LOAD AIR POLLUTION DATA ---------------------
    air_path = os.path.join(settings.BASE_DIR, "aqiApplication", "dataset", "air_pollution_data.csv")
    df = pd.read_csv(air_path)

    # ------------------ 2. LOAD STATION DATA ---------------------------
    stations_path = os.path.join(settings.BASE_DIR, "aqiApplication", "dataset", "stations.csv")
    stations = pd.read_csv(stations_path)

    # ------------------ 3. LOAD 2015–2020 CITY DATA --------------------
    cityday_path = os.path.join(settings.BASE_DIR, "aqiApplication", "dataset", "city_day.csv")
    df_cityday = pd.read_csv(cityday_path)

    # ====================== DELHI YEARLY AQI CHART ======================
    delhi = df_cityday[df_cityday["City"] == "Delhi"].copy()
    delhi["Date"] = pd.to_datetime(delhi["Date"])
    delhi["Year"] = delhi["Date"].dt.year

    # Group by year
    delhi_yearly = delhi.groupby("Year")["AQI"].mean().reset_index()

    plt.figure(figsize=(10, 5))
    matplotlib.pyplot.close()
    sns.lineplot(data=delhi_yearly, x="Year", y="AQI", marker="o")
    plt.title("Delhi AQI Variation (2015–2020)")
    plt.xticks(delhi_yearly["Year"])
    delhi_chart_path = os.path.join(charts_dir, "delhi_aqi.png")
    plt.tight_layout()
    plt.savefig(delhi_chart_path)
    plt.clf()

    # ====================== AVERAGE AQI BY CITY =========================
    plt.figure(figsize=(10, 5))
    city_aqi = df.groupby("city")["aqi"].mean().reset_index()
    sns.barplot(data=city_aqi, x="city", y="aqi")
    plt.xticks(rotation=45)
    aqi_bar_path = os.path.join(charts_dir, "aqi_bar.png")
    plt.tight_layout()
    plt.savefig(aqi_bar_path)
    plt.clf()

    # ====================== STATION COUNT BY STATE ======================
    plt.figure(figsize=(10, 5))
    state_count = stations["State"].value_counts()
    sns.barplot(x=state_count.index, y=state_count.values)
    plt.xticks(rotation=45)
    state_bar_path = os.path.join(charts_dir, "state_station_bar.png")
    plt.tight_layout()
    plt.savefig(state_bar_path)
    plt.clf()

    # ====================== ACTIVE VS INACTIVE PIE ======================
    status_count = stations["Status"].fillna("Inactive").value_counts()

    plt.figure(figsize=(6, 6))
    plt.pie(status_count, labels=status_count.index, autopct='%1.1f%%')
    status_pie_path = os.path.join(charts_dir, "status_pie.png")
    plt.tight_layout()
    plt.savefig(status_pie_path)
    plt.clf()

    # ====================== SEND TO TEMPLATE =============================
    context = {
        "delhi_aqi": "charts/delhi_aqi.png",
        "aqi_bar": "charts/aqi_bar.png",
        "state_station_bar": "charts/state_station_bar.png",
        "status_pie": "charts/status_pie.png",
    }

    return render(request, "air_app/dashboard.html", context)

def safety(request):
    return render(request, "air_app/safety.html")
