from datetime import date, timedelta
from statistics import mean

import streamlit as st

import queries
import visualization


def main():
    st.title("Daily air pollution")
    st.write('''
            ### Select a place in France
            Identify the air quality monitoring station whose pollution data you are interested in.
            ''')
    st.session_state["y-values"] = [[0 for e in range(24)],[0 for e in range(24)]]
    st.session_state["first_choice"] = True
    st.session_state["no_data"] = True

    def update_values(station: str, pollutant: str) -> None:
        start = st.session_state["start"]
        working_days, weekends = queries.get_data(station, pollutant)
        counter = 0
        for i, data in enumerate([working_days, weekends]):
            if data:
                # Initialize "dictionary" which will contain the average
                # concentration values (set to zero when no data are
                # available) associated to the 24 hours of the day.
                dictionary = {str(x): 0 for x in range(24)}
                for document in data:
                    # Get the hour of the day treated by the current document.
                    hour = document["_id"]["hour"]
                    # Extract only air concentration values being less than
                    # "n_days" days old.
                    history = list(zip(
                        document["history"]["values"],
                        document["history"]["dates"]))[::-1]
                    j = 0
                    limit = len(history)
                    while (
                        j < limit and 
                        (start <= history[j][1].date())):
                        j += 1
                    if j == limit:
                        j -= 1
                    # Update "dictionary".
                    dictionary[str(hour)] = \
                    mean([e[0] for e in history[:j]])
                st.session_state["y-values"][i] = list(dictionary.values())
            else:
                counter += 1
        if counter < 2:
            st.session_state["no_data"] = False
    
    col1, col2 = st.columns((5,1))
    with col1:

        kwargs = {"index": None, "placeholder": ""}
        
        try:
            region = st.selectbox(
                "Select a French region",
                queries.get_items("regions", {}),
                **kwargs)
        
            department = st.selectbox(
                "Select a French department",
                queries.get_items("departments", {"_id": region}),
                **kwargs)
        
            city = st.selectbox(
                "Select a French city",
                queries.get_items("cities", {"_id": department}),
                **kwargs)
        
            available_stations = list(map(
                lambda x: x.split("#"),
                queries.get_items("stations", {"_id": city})))
            names = [e[0] for e in available_stations]
            station = st.selectbox(
                "Select a station",
                names,
                **kwargs)
            
            if station not in queries.get_stations():
                st.error("Sorry, no data available for this station.")
                st.stop()
            else:
                pollution = st.selectbox(
                    "Select a type of pollution",
                    queries.get_items("pollutants", {"_id": station}),
                    **kwargs)
            
                pollutant = pollution.split()[0]
                
                first_date, last_date = queries.get_dates()
            
                if st.session_state["first_choice"]:
                    update_values(station, pollutant)
                    st.session_state["first_choice"] = False

                if st.session_state["no_data"]:
                    st.error("No pollution data are available for the given period.")
                    st.stop()
                else:
                    st.pyplot(
                        visualization.plot_variation(
                            st.session_state["y-values"],
                            pollutant,
                            station))

                    first_date, last_date = queries.get_dates()
                    start = st.slider(
                        "When does the air pollution analysis start?",
                        first_date,
                        last_date,
                        last_date-timedelta(days=90),
                        format="DD/MM/YY",
                        key="start",
                        on_change=update_values,
                        args=(station, pollutant))
        except:
            st.stop()

if __name__=="__main__":
    main()
