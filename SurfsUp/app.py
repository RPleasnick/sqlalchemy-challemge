# Import the dependencies.
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
import pandas as pd


#################################################
# Database Setup
#################################################

# import os
# print(os.getcwd())

engine = create_engine(r"sqlite+pysqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

# route for Homepage
@app.route("/")
def welcome():
    # """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startYYYY-MM-DD<start><br/>"
        f"/api/v1.0/startYYYY-MM-DD<start>/endYYYY-MM-DD<end><br/>"
    )

#route for precipitation
@app.route("/api/v1.0/precipitation")
def precipitation_route():
    session = Session(engine)

   # Find the most recent date in the data set.
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Calculate the date one year from the last date in data set.
    year_later = pd.to_datetime(most_recent_date[0]) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_later.date()).all()

    session.close()

    # Convert query results to dictionary
    precipitation_dict = {}
    for result in results:
        precipitation_dict[result[0]] = result[1] # result[0]=date, result[1]=prcp

    # Return jsonified results
    return jsonify(precipitation_dict)



#route for stations
@app.route("/api/v1.0/stations")
def station_route():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # """Return a list of all stations"""
    # Query all passengers
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    stations = list(results)

    station_list =[]
    for item in stations:
        station_list.append(item[0])
    
    return jsonify(station_list)


#route for tobs
@app.route("/api/v1.0/tobs")
def tobs_route():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # """Return dates and temperatures of the most active station"""
    # Design a query to find the most active stations (i.e. which stations have the most rows?)
    # Find the most active station.
    most_active = session.query((Measurement.station), func.count(Measurement.station)).group_by(Measurement.station) \
        .order_by(func.count(Measurement.station).desc()).first()[0]
    
    # Query the last 12 months of temperature observation data for this station
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).filter(Measurement.station == most_active).first()

    most_active_temps = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active).\
            filter(Measurement.date >= func.date((max_date[0]), '-12 months')).all()

    session.close()

    # Convert query results to dictionary
    most_active_dict = {}
    for result in most_active_temps:
        most_active_dict[result[0]] = result[1] # result[0]=date, result[1]=temp

    
    return jsonify(most_active_dict)


#route for temperature stats for given date 
@app.route("/api/v1.0/start<start>")
def start_date_route(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # """Return temperature min, ave, and max"""
    date_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date == start).all()
    
    session.close()

    # Create a dictionary
    date_stats_dict = {
        'Min': date_stats[0][0],
        'Avg': date_stats[0][1],
        'Max': date_stats[0][2]
    }
    return jsonify(date_stats_dict)

#route for temperature stats for given date range
@app.route('/api/v1.0/start<start>/end<end>')
def range_date_route(start, end):
    session = Session(engine)

    date_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
    .filter(Measurement.date >= start, Measurement.date <= end).all()
    
    session.close()

    # Create a dictionary
    range_stats_dict = {
        'Min': date_stats[0][0],
        'Avg': date_stats[0][1],
        'Max': date_stats[0][2]
    }
    return jsonify(range_stats_dict)



if __name__ == '__main__':
    app.run(debug=True)
