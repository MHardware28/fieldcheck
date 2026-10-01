import requests
import pandas as pd
import streamlit as st

ICONS = {"Go": "✅ Go", "Caution": "⚠️ Caution", "No-Go": "⛔ No-Go"}
ORDER = {"Go": 0, "Caution": 1, "No-Go": 2}


@st.cache_data(ttl=3600)
def find_city(name):
    """Returns a DataFrame of matches (empty if none), or None if the request failed."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    try:
        r = requests.get(url, params={"name": name, "count": 5}, timeout=10)
        r.raise_for_status()
        return pd.DataFrame(r.json().get("results", []))
    except requests.RequestException:
        return None


@st.cache_data(ttl=1800)
def get_forecast(lat, lon):
    """Hourly forecast for 7 days. Returns None if the request failed."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "apparent_temperature,precipitation_probability,wind_speed_10m,wind_gusts_10m,weather_code",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "forecast_days": 7,
        "timezone": "auto",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        df = pd.DataFrame(r.json()["hourly"])
    except (requests.RequestException, KeyError):
        return None

    df = df.rename(columns={
        "apparent_temperature": "feels_like",
        "precipitation_probability": "rain_chance",
        "wind_speed_10m": "wind",
        "wind_gusts_10m": "gusts",
    })
    df["time"] = pd.to_datetime(df["time"])
    df["date"] = df["time"].dt.date
    df["hour"] = df["time"].dt.hour
    return df


@st.cache_data
def load_thresholds():
    return pd.read_csv("data/thresholds.csv")


def thresholds_ready(th):
    # True if at least one threshold has been filled in
    return th[["caution_at", "nogo_at"]].notna().any().any()


def rate_hour(row, th):
    # Open-Meteo weather codes 95-99 are thunderstorms
    if row["weather_code"] >= 95:
        return "No-Go"
    result = "Go"
    for _, t in th.iterrows():
        value = row[t["metric"]]
        if pd.notna(t["nogo_at"]) and value >= t["nogo_at"]:
            return "No-Go"
        if pd.notna(t["caution_at"]) and value >= t["caution_at"]:
            result = "Caution"
    return result


def add_ratings(df, th):
    df = df.copy()
    df["rating"] = df.apply(rate_hour, axis=1, th=th)
    return df


def worst_rating(ratings):
    return max(ratings, key=lambda r: ORDER[r])
