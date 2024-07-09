import streamlit as st
import pandas as pd
import altair as alt
from streamlit_autorefresh import st_autorefresh

from utils.anedya import anedya_config
from utils.anedya import anedya_getValue
from utils.anedya import fetchHumidityData
from utils.anedya import fetchTemperatureData
from utils.anedya import fetchUVIndexData
from utils.anedya import fetchPressureData
from utils.anedya import fetchSoilMoistureData

# nodeId = "20deeee8-f8ae-11ee-9dd8-c3aa61afe2fb"  # get it from anedya dashboard -> project -> node 
nodeId = "161a1a42-3778-11ef-9ecc-a1461caa74a3"  # get it from anedya dashboard -> project -> node 
apiKey = "676a52651a23a1cd891a78d15814bc2ebdd88921e1eca62ddedb505d9ab39b17"  # aneyda project apikey

st.set_page_config(page_title="Weather Monitoring and Reporting System", layout="wide", page_icon=":partly_sunny:")

# Uncomment to show count
# count = st_autorefresh(interval=30000, limit=None, key="auto-refresh-handler")
st_autorefresh(interval=30000, limit=None, key="auto-refresh-handler")

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: white;
        color: black;
    }
    header {
        background-color: black;
        color: orange;
    }
    .css-18e3th9 {
        background-color: black;
        color: orange;
    }
    .css-1d391kg {
        background-color: black;
        color: orange;
    }
    h1 {
        color: orange;
    }
    h2, h3, h4, h5, h6 {
        color: black;
    }
</style>
""", unsafe_allow_html=True)

# --------------- HELPER FUNCTIONS -----------------------
def V_SPACE(lines):
    for _ in range(lines):
        st.write("&nbsp;")

humidityData = pd.DataFrame()
temperatureData = pd.DataFrame()
uvData = pd.DataFrame()
soilData = pd.DataFrame()
pressureData = pd.DataFrame()

def main():
    global humidityData, temperatureData, uvData, soilData, pressureData
    anedya_config(NODE_ID=nodeId, API_KEY=apiKey)

    if "CurrentHumidity" not in st.session_state:
        st.session_state.CurrentHumidity = 0

    if "CurrentTemperature" not in st.session_state:
        st.session_state.CurrentTemperature = 0

    if "CurrentUV" not in st.session_state:
        st.session_state.CurrentUV = 0

    if "Currentpressure" not in st.session_state:
        st.session_state.Currentpressure = 0

    if "CurrentSoilMoisture" not in st.session_state:
        st.session_state.CurrentSoilMoisture = 0

    humidityData = fetchHumidityData()
    temperatureData = fetchTemperatureData()
    uvData = fetchUVIndexData()
    soilData = fetchSoilMoistureData()
    pressureData = fetchPressureData()

    drawDashboard()

def drawDashboard():
    headercols = st.columns([1, 0.1, 0.1], gap="small")
    with headercols[0]:
        st.title("Weather Monitoring and Reporting System", anchor=False)
    with headercols[1]:
        st.button("Refresh")

    st.markdown("This dashboard provides a live view of Himanshu Room temperature and humidity.")

    st.subheader(body="Current Status", anchor=False)
    cols = st.columns(3, gap="medium")
    with cols[0]:
        st.metric(label="Humidity", value=str(st.session_state.CurrentHumidity) + " % 💧")
    with cols[1]:
        st.metric(label="Temperature", value=str(st.session_state.CurrentTemperature) + " °C 🌡️")
    with cols[2]:
        st.metric(label="UV Index", value=str(st.session_state.CurrentUV) + " UV ☀️")
    with cols[0]:
        st.metric(label="Soil Moisture", value=str(st.session_state.CurrentSoilMoisture) + " % 🌱")
    with cols[1]:
        st.metric(label="Pressure", value=str(st.session_state.Currentpressure) + " hPa 🌬️")    

    charts = st.columns(3, gap="small")
    with charts[0]:
        st.subheader(body="Humidity", anchor=False)
        if humidityData.empty:
            st.write("No Data !!")
        else:
            humidity_chart_an = alt.Chart(data=humidityData).mark_area(
                line={'color': '#1fa2ff'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#1fa2ff', offset=1),
                           alt.GradientStop(color='rgba(255,255,255,0)', offset=0)],
                    x1=1,
                    x2=1,
                    y1=1,
                    y2=0,
                ),
                interpolate='monotone',
                cursor='crosshair'
            ).encode(
                x=alt.X(
                    shorthand="Datetime:T",
                    axis=alt.Axis(format="%Y-%m-%d %H:%M:%S", title="Datetime", tickCount=10, grid=True, tickMinStep=5),
                ),  # T indicates temporal (time-based) data
                y=alt.Y(
                    "aggregate:Q",
                    scale=alt.Scale(domain=[10, 100]),
                    axis=alt.Axis(title="Humidity (%)", grid=True, tickCount=10),
                ),  # Q indicates quantitative data
                tooltip=[alt.Tooltip('Datetime:T', format="%Y-%m-%d %H:%M:%S", title="Time"),
                         alt.Tooltip('aggregate:Q', format="0.2f", title="Value")],
            ).properties(height=400).interactive()

            st.altair_chart(humidity_chart_an, use_container_width=True)

    with charts[1]:
        st.subheader(body="Temperature", anchor=False)
        if temperatureData.empty:
            st.write("No Data !!")
        else:
            temperature_chart_an = alt.Chart(data=temperatureData).mark_area(
                line={'color': '#1fa2ff'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#1fa2ff', offset=1),
                           alt.GradientStop(color='rgba(255,255,255,0)', offset=0)],
                    x1=1,
                    x2=1,
                    y1=1,
                    y2=0,
                ),
                interpolate='monotone',
                cursor='crosshair'
            ).encode(
                x=alt.X(
                    shorthand="Datetime:T",
                    axis=alt.Axis(format="%Y-%m-%d %H:%M:%S", title="Datetime", tickCount=10, grid=True, tickMinStep=5),
                ),  # T indicates temporal (time-based) data
                y=alt.Y(
                    "aggregate:Q",
                    scale=alt.Scale(zero=False, domain=[10, 50]),
                    axis=alt.Axis(title="Temperature (°C)", grid=True, tickCount=10),
                ),  # Q indicates quantitative data
                tooltip=[alt.Tooltip('Datetime:T', format="%Y-%m-%d %H:%M:%S", title="Time"),
                         alt.Tooltip('aggregate:Q', format="0.2f", title="Value")],
            ).properties(height=400).interactive()

            st.altair_chart(temperature_chart_an, use_container_width=True)
    
    with charts[2]:
        st.subheader(body="Soil Moisture", anchor=False)
        if soilData.empty:
            st.write("No Data !!")
        else:
            soil_chart_an = alt.Chart(data=soilData).mark_area(
                line={'color': '#1fa2ff'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#1fa2ff', offset=1),
                           alt.GradientStop(color='rgba(255,255,255,0)', offset=0)],
                    x1=1,
                    x2=1,
                    y1=1,
                    y2=0,
                ),
                interpolate='monotone',
                cursor='crosshair'
            ).encode(
                x=alt.X(
                    shorthand="Datetime:T",
                    axis=alt.Axis(format="%Y-%m-%d %H:%M:%S", title="Datetime", tickCount=10, grid=True, tickMinStep=5),
                ),  # T indicates temporal (time-based) data
                y=alt.Y(
                    "aggregate:Q",
                    scale=alt.Scale(domain=[10, 100]),
                    axis=alt.Axis(title="Soil Moisture (%)", grid=True, tickCount=10),
                ),  # Q indicates quantitative data
                tooltip=[alt.Tooltip('Datetime:T', format="%Y-%m-%d %H:%M:%S", title="Time"),
                         alt.Tooltip('aggregate:Q', format="0.2f", title="Value")],
            ).properties(height=400).interactive()

            st.altair_chart(soil_chart_an, use_container_width=True)

    charts = st.columns(2, gap="small")
    with charts[0]:
        st.subheader(body="UV Index", anchor=False)
        if uvData.empty:
            st.write("No Data !!")
        else:
            uv_chart_an = alt.Chart(data=uvData).mark_area(
                line={'color': '#1fa2ff'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#1fa2ff', offset=1),
                           alt.GradientStop(color='rgba(255,255,255,0)', offset=0)],
                    x1=1,
                    x2=1,
                    y1=1,
                    y2=0,
                ),
                interpolate='monotone',
                cursor='crosshair'
            ).encode(
                x=alt.X(
                    shorthand="Datetime:T",
                    axis=alt.Axis(format="%Y-%m-%d %H:%M:%S", title="Datetime", tickCount=10, grid=True, tickMinStep=5),
                ),  # T indicates temporal (time-based) data
                y=alt.Y(
                    "aggregate:Q",
                    scale=alt.Scale(domain=[0, 15]),
                    axis=alt.Axis(title="UV Index", grid=True, tickCount=10),
                ),  # Q indicates quantitative data
                tooltip=[alt.Tooltip('Datetime:T', format="%Y-%m-%d %H:%M:%S", title="Time"),
                         alt.Tooltip('aggregate:Q', format="0.2f", title="Value")],
            ).properties(height=400).interactive()

            st.altair_chart(uv_chart_an, use_container_width=True)

    with charts[1]:
        st.subheader(body="Pressure", anchor=False)
        if pressureData.empty:
            st.write("No Data !!")
        else:
            pressure_chart_an = alt.Chart(pressureData).mark_area(
                line={'color': '#1fa2ff'},
                color=alt.Gradient(
                    gradient='linear',
                    stops=[alt.GradientStop(color='#1fa2ff', offset=1),
                           alt.GradientStop(color='rgba(255,255,255,0)', offset=0)],
                    x1=1,
                    x2=1,
                    y1=1,
                    y2=0,
                ),
                interpolate='monotone',
                cursor='crosshair'
            ).encode(
                x=alt.X(
                    shorthand="Datetime:T",
                    axis=alt.Axis(format="%Y-%m-%d %H:%M:%S", title="Datetime", tickCount=10, grid=True, tickMinStep=5),
                ),  # T indicates temporal (time-based) data
                y=alt.Y(
                    "aggregate:Q",
                    scale=alt.Scale(domain=[900, 1100]),
                    axis=alt.Axis(title="Pressure (hPa)", grid=True, tickCount=10),
                ),  # Q indicates quantitative data
                tooltip=[alt.Tooltip('Datetime:T', format="%Y-%m-%d %H:%M:%S", title="Time"),
                         alt.Tooltip('aggregate:Q', format="0.2f", title="Value")],
            ).properties(height=400).interactive()

            st.altair_chart(pressure_chart_an, use_container_width=True)
            
if __name__ == "__main__":
    main()
