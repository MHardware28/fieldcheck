import streamlit as st
from utils import load_thresholds

#This entire page is just a reference for the user which lets them know what each limit means.
st.title("Safety Guide")
st.write("These are the limits FieldCheck uses, and where each one comes from.")

th = load_thresholds()
if th[["caution_at", "nogo_at"]].isna().all().all():
    st.info("Thresholds haven't been added yet.")
else:
    st.dataframe(th)

st.divider()
st.subheader("What each rule means")


def show_limits(metric, unit):
    # Shows the numbers from thresholds.csv so this page always matches the app
    row = th[th["metric"] == metric].iloc[0]
    if row["caution_at"] != row["caution_at"] and row["nogo_at"] != row["nogo_at"]:
        st.caption("No limit has been set for this yet.")
        return
    if row["caution_at"] == row["caution_at"]:
        st.write(f"⚠️ **Caution** at {row['caution_at']} {unit} or higher")
    if row["nogo_at"] == row["nogo_at"]:
        st.write(f"⛔ **No-Go** at {row['nogo_at']} {unit} or higher")
    if row["source"] == row["source"]:
        st.caption(f"Source: {row['source']}")

#all these expanders are just for reference and do not affect the app in any way. They are meant to give the user more information about what each limit means and where it comes from.
with st.expander("⚡ Lightning and thunderstorms"):
    st.write(
        "If you can hear thunder, lightning is close enough to be dangerous. "
        "The National Weather Service advises moving everyone indoors when you hear thunder "
        "and waiting 30 minutes after the last thunder before going back out. "
        "FieldCheck marks any hour with a thunderstorm in the forecast as No-Go."
    )
    st.caption("Source: National Weather Service lightning safety, weather.gov/safety/lightning")

with st.expander("🌡️ Heat (feels-like temperature)"):
    st.write(
        "Feels-like temperature combines heat and humidity, so it is a better guide "
        "than the number on a thermometer. Athletes lose the ability to cool off when it is "
        "hot and humid, which raises the risk of heat illness. When the number is high, "
        "consider shorter practices, more water breaks, shade, or moving practice to a cooler hour."
    )
    show_limits("feels_like", "°F")

with st.expander("💨 Wind and gusts"):
    st.write(
        "Steady wind can make cold days feel colder and affect drills like passing, kicking, "
        "and throwing. Gusts are the sudden peaks. Strong gusts matter for safety around "
        "equipment like goals, nets, tents, and batting cages."
    )
    show_limits("wind", "mph")
    show_limits("gusts", "mph")

with st.expander("🌧️ Chance of rain"):
    st.write(
        "This is the forecast chance that measurable rain falls during that hour. "
        "It is not how hard it will rain. Wet fields can also be slippery, "
        "so check your field conditions in person."
    )
    show_limits("rain_chance", "%")

st.info(
    "FieldCheck is just a planning tool built to help coaches. "
    "The coach or trainer in charge of practice makes the final call."
)
