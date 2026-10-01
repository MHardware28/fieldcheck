import streamlit as st
from utils import find_city

st.set_page_config(page_title="FieldCheck", page_icon="🏟️")

st.title("🏟️ FieldCheck")
st.subheader("Is it a good day to practice outside?")

st.write("""
**Who it's for:** Coaches at any level who run practices on outdoor fields.

**The problem:** A regular weather app shows a high temperature and a rain icon.
Though a regular weather app might show these conditions, it doesn't provide information about the specific impact on outdoor practices.

**Why it matters:** Bad calls put athletes at risk, or waste practice time when
a coach cancels too cautiously.
""")

st.divider()
st.header("Set up your practice")

city = st.text_input("City", value=st.session_state.get("city_query", ""))

if city:
    st.session_state["city_query"] = city
    matches = find_city(city)

    if matches is None:
        st.error("Couldn't reach the weather service. Please try again in a minute.")
    elif matches.empty:
        st.warning("We couldn't find that city. Check the spelling or try a nearby larger city.")
    else:
        matches["label"] = matches["name"] + ", " + matches["admin1"].fillna("") + ", " + matches["country"]
        choice = st.selectbox("Which one?", matches["label"])
        row = matches[matches["label"] == choice].iloc[0]
        st.session_state["lat"] = row["latitude"]
        st.session_state["lon"] = row["longitude"]
        st.session_state["place"] = choice

sports = ["Lacrosse", "Football", "Baseball/Softball", "Track", "Soccer", "Other"]
sport = st.selectbox(
    "Sport", sports, index=sports.index(st.session_state.get("sport", "Lacrosse"))
)
st.session_state["sport"] = sport

start, end = st.slider(
    "Practice window (hour of day, 24h)",
    0, 23,
    (st.session_state.get("start_hour", 5), st.session_state.get("end_hour", 7)),
)
st.session_state["start_hour"] = start
st.session_state["end_hour"] = end

if "lat" in st.session_state:
    st.success(f"Saved: {st.session_state['place']}. Open Today's Check in the sidebar.")
