import streamlit as st
from utils import get_forecast, load_thresholds, thresholds_ready, add_ratings, worst_rating, ICONS

st.title("Today's Check")
#alerts you if they havent selected the city and/practice times yet.
if "lat" not in st.session_state:
    st.warning("Set your city and practice window on the Home page first.")
    st.stop()

th = load_thresholds()
if not thresholds_ready(th):
    st.warning("No thresholds have been added yet, so only thunderstorms are checked.")

df = get_forecast(st.session_state["lat"], st.session_state["lon"])
if df is None:
    st.error("Couldn't load the forecast. Please try again in a minute.")
    st.stop()

df = add_ratings(df, th)
today = df["date"].min()
start = st.session_state["start_hour"]
end = st.session_state["end_hour"]
window = df[(df["date"] == today) & (df["hour"] >= start) & (df["hour"] <= end)]

if window.empty:
    st.info("No forecast hours fall inside your practice window today.")
    st.stop()

#prints the selected city from the home page as well as the practice window.
st.write(f"**{st.session_state['place']}** · {st.session_state['sport']} · {start}:00 to {end}:00")

#prints the verdict and the icon associated with it.
verdict = worst_rating(window["rating"])
st.header(ICONS[verdict])

#gives a quick overview of the ratings during the practice window that was selected.
good_hours = (window["rating"] == "Go").sum()
col1, col2, col3 = st.columns(3)
col1.metric("Hottest feels-like (°F)", round(window["feels_like"].max()))
col2.metric("Windiest gust (mph)", round(window["gusts"].max()))
col3.metric("Good hours", f"{good_hours} of {len(window)}")

#creates dropdown that shows a table listing out the hours of practice and what to expect.
with st.expander("Why this verdict?"):
    st.write("The verdict is the worst rating of any hour in your window.")
    st.dataframe(window[["hour", "feels_like", "rain_chance", "wind", "gusts", "rating"]])

#creates tabs that show the feels-like temperature, wind and gusts, and chance of rain during the practice window.
tab1, tab2, tab3 = st.tabs(["Temperature", "Wind", "Rain"])
chart_data = window.set_index("hour")
with tab1:
    st.bar_chart(chart_data["feels_like"])
with tab2:
    st.bar_chart(chart_data[["wind", "gusts"]])
with tab3:
    st.line_chart(chart_data["rain_chance"])
