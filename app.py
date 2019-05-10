import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request

import datetime as dt
from datetime import date

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
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
    """List all available api routes."""
    return (
        f"Home page<br/>"
        f"All Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Or You can enter just start date or start/end dates (between '2010-01-01' & '2017-08-23'):<br/>"
        f"Example:<br/>"
        f"/api/v1.0/2015-06-08<br/>"
        f"OR<br/>"
        f"/api/v1.0/2015-06-08/2015-09-08<br/>"
    )


@app.route("/api/v1.0/precipitation")

def precipitation():
    """ retrieve precipitation data from one year period as dictionary in format {key:date, value:prcp}"""
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.datetime.strptime(max_date[0], "%Y-%m-%d") - dt.timedelta(days=366)
    
    precipitation_query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).order_by(Measurement.date).all()
    

    return jsonify(precipitation_query)


@app.route("/api/v1.0/stations")

def stations():
    """Return a JSON list of stations from the dataset."""
    # Query all stations
    query_stations =  session.query(Measurement.station).group_by(Measurement.station).all()

    # Convert list of tuples into normal list
    #stations_list = list(np.ravel(query_stations))

    return jsonify(query_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Query for the dates and temperature observations from a year from the last data point."""
    # find a year ago date
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.datetime.strptime(max_date[0], "%Y-%m-%d") - dt.timedelta(days=366)
    
    query_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()

    return jsonify(query_tobs)


@app.route('/api/v1.0/<start>')
def start(start=None):
    """Start only --> calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""
    start_query = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    

    # Create list of dictionaries iterating through query data
    start_list = []
    for i in range(len(start_query)):
        temp_dict = {}
        temp_dict["date"] = start_query[i][0]
        temp_dict["min_temp"] = start_query[i][1]
        temp_dict["avg_temp"] = start_query[i][2]
        temp_dict["max_temp"] = start_query[i][3]
        start_list.append(temp_dict)
    
    return jsonify(start_list)


@app.route('/api/v1.0/<start>/<end>')
def date_range(start=None, end=None):
    """Start and the end date --> calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
    start_end_query = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    
    start_end_list = []
    for i in range(len(start_end_query)):
        temp_dict = {}
        temp_dict["date"] = start_end_query[i][0]
        temp_dict["min_temp"] = start_end_query[i][1]
        temp_dict["avg_temp"] = start_end_query[i][2]
        temp_dict["max_temp"] = start_end_query[i][3]
        start_end_list.append(temp_dict)

    return jsonify(start_end_list)


if __name__ == '__main__':
    app.run(debug=True)