# Import the dependencies.
# import datetime as dt
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################

# engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# absolute path below was used do to operational errors
engine = create_engine("sqlite:///C:/Users/robby/Downloads/Class work/Starter_Code moduel 10/Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"
    )
# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in the data set
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    results = session.query(Station.station).all()

    # Convert the query results to a list
    station_list = list(np.ravel(results))

    return jsonify(station_list)

# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most recent date in the data set.
    most_recent_date = session.query(func.max(Measurement.date)).scalar()

    # Calculate the date one year from the last date in the data set
    one_year_ago = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query temperature observations for the most active station for the previous year
    # Find the most active station
    most_active_station = (
    session.query(Measurement.station, func.count(Measurement.station).label('station_count'))
    .group_by(Measurement.station)
    .order_by(func.count(Measurement.station).desc())
    .first()
).station

    results = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == most_active_station,
        Measurement.date >= one_year_ago
    ).all()

    # Convert the query results to a list of dictionaries
    tobs_data = [{"Date": date, "Temperature": tobs} for date, tobs in results]

    return jsonify(tobs_data)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature
# for a specified start or start-end range.
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def temp_range(start, end=None):
    # Convert start and end dates to datetime objects
    start_date = dt.datetime.strptime(start, "%m%d%Y")
    end_date = dt.datetime.strptime(end, "%m%d%Y") if end else dt.datetime.now()

    # Query temperature statistics for the specified date range
    results = session.query(
        func.min(Measurement.tobs).label('min_temperature'),
        func.avg(Measurement.tobs).label('avg_temperature'),
        func.max(Measurement.tobs).label('max_temperature')
    ).filter(Measurement.date.between(start_date, end_date)).all()

    # Convert the query results to a dictionary
    temperature_stats_data = {
        "Start Date": start_date.strftime("%Y-%m-%d"),
        "End Date": end_date.strftime("%Y-%m-%d") if end else None,
        "Min Temperature": results[0].min_temperature,
        "Avg Temperature": results[0].avg_temperature,
        "Max Temperature": results[0].max_temperature
    }

    return jsonify(temperature_stats_data)

if __name__ == '__main__':
    app.run(debug=True)