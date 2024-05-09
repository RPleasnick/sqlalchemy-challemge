# Import the dependencies.
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite+pysqlite:///SurfsUp/Resources/hawaii.sqlite")

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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        # f"/api/v1.0/<start><br/>"
        # f"/api/v1.0/<start>/<end><br/>"
    )

#route for precipitation
@app.route("/api/v1.0/precipitation")
def precipitation_data():
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
def station_list():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all passengers
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    stations = list(results)

    return jsonify(stations)


#route for tobs
@app.route("/api/v1.0/tobs")
def station_list():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return dates and temperatures of the most active station"""
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

    
    return jsonify(tobs_dates)



if __name__ == '__main__':
    app.run(debug=True)
