import streamlit as st
from utils import get_forecast, load_thresholds, add_ratings

st.title("Week Planner")

if "lat" not in st.session_state:
    st.warning("Set your city and practice window on the Home page first.")
    st.stop()

df = get_forecast(st.session_state["lat"], st.session_state["lon"])
if df is None:
    st.error("Couldn't load the forecast. Please try again in a minute.")
    st.stop()

df = add_ratings(df, load_thresholds())

st.sidebar.header("Filters")
days = st.sidebar.multiselect("Days", sorted(df["date"].unique()), default=sorted(df["date"].unique()))
start, end = st.sidebar.slider(
    "Hours", 0, 23, (st.session_state["start_hour"], st.session_state["end_hour"])
)
only_go = st.sidebar.checkbox("Only show good hours")

view = df[df["date"].isin(days) & (df["hour"] >= start) & (df["hour"] <= end)]
if only_go:
    view = view[view["rating"] == "Go"]

if view.empty:
    st.info("No hours match these filters. Try picking more days or a wider window.")
    st.stop()

st.subheader("Hours by rating, per day")
counts = view.groupby(["date", "rating"]).size().unstack(fill_value=0)
st.bar_chart(counts)

st.subheader("Hourly detail")
st.dataframe(view[["time", "feels_like", "rain_chance", "wind", "gusts", "rating"]].sort_values("time"))
