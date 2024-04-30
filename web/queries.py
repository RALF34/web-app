from datetime import date, timedelta
from typing import Dict, List, Tuple

from pymongo import collection, MongoClient
import streamlit as st

OVERSEAS_DEPARTMENTS = [
    "GUADELOUPE",
    "GUYANE",
    "MARTINIQUE",
    "LA REUNION",
    "MAYOTTE",
    "SAINT-MARTIN"]


@st.cache_resource
def init_connection():
    return MongoClient(
        host="db",
        authSource="air_quality")

@st.cache_data
def get_stations() -> List[str]:
    database = init_connection()["air_quality"]
    return database["distribution_pollutants"].distinct("_id")

def get_data(s: str, p: str) -> List[collection]:
    '''
    Return the pymongo collections (or None when not enough data) 
    containing hourly average air concentrations of pollutant "p" 
    recorded by station "s" on both working_days and weekends.
    '''
    database = init_connection()["air_quality"]
    query_filter = {
        "_id.station":s,
        "_id.pollutant": p}
    data = [
        database[name].find(query_filter) for name in
        ["working_days", "weekends"]]
    return data

def get_items(
    about: str, 
    query_filter: Dict[str, str]) -> List[str]:
    '''
    Query the "air_quality" database to retrieve the items
    representing the available choices proposed to the user.

    Arguments:
    about -- string determining the name of the collection
             to query within the database.
    query_filter -- dictionary used as filter for the query.
    '''
    database = init_connection()["air_quality"]
    # Query the appropriate collection and store the retrieved
    # elements in a list "items".
    match about:
        case "regions":
            items = database["regions"].find().distinct("_id")
            for e in OVERSEAS_DEPARTMENTS:
                items.remove(e)
            items.append("OUTRE-MER")
        case "departments":
            if query_filter["_id"] == "OUTRE-MER":
                items = OVERSEAS_DEPARTMENTS
            else:
                items = list(set(database["regions"].find_one(
                    query_filter)["departments"]))
        case "cities":
            items = list(set(database["departments"].find_one(
                query_filter)["cities"]))
        case "stations":
            stations = database["cities"].find_one(
                query_filter)["stations"]
            items = [
                e["name"]+"#"+
                str(e["coordinates"]["latitude"])+
                "-"+str(e["coordinates"]["longitude"]) 
                for e in stations]
        case "pollutants":
            pollutants = list(set(database["distribution_pollutants"].find_one(
                query_filter)["monitored_pollutants"]))
            items = [e+" pollution" for e in pollutants]
    return items

def get_dates() -> Tuple[date, date]:
    '''
    Return the starting and the ending dates of the period over which
    the pollution data are collected.
    '''
    database = init_connection()["air_quality"]
    last_update = database["last_update"].find_one()["date"]
    ending_date = date(
        last_update.year,
        last_update.month,
        last_update.day)
    starting_date = ending_date - timedelta(days=180)
    return starting_date, ending_date
