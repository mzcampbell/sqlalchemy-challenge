import numpy as np

#import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt 
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station



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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br>"
        f"/api/v1.0/start/end<br>"
    )

#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    """Return a list of rain fall for prior year"""
    # Find the most recent date in the data set.
    row=(session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    most_recent_date=dt.datetime.strptime(row[0], '%Y-%m-%d')
    # Calculate the date one year from the last date in data set.
    last_year=most_recent_date - dt.timedelta(days=366)
    print(most_recent_date)
    print(last_year)
    # Perform a query to retrieve the data and precipitation scores
    last_year_precip_scores=session.query(Measurement.date, Measurement.prcp)\
                            .filter(Measurement.date >last_year)\
                            .group_by(Measurement.date)\
                            .all()
    
    #Create a list of dictionaries with date and prcp as keys
    precip_scores = []
    for most_recent_date in last_year_precip_scores:
        row={}
        row["date"] = last_year_precip_scores[0]
        row["prcp"] = last_year_precip_scores[1]
        precip_scores.append(row)
    
    session.close()
    print(precip_scores)
    return jsonify(precip_scores)

    

#################################################
    


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    stations_query=session.query(Station.name, Station.station)
    #Create a list of dictionaries
    stations = []
    for x in stations_query:
        row = {}
        row["name"] = x[0]
        row["station"] = x[1]
        stations.append(row)
    
    session.close()

    return jsonify(stations)

    

    
#################################################
@app.route("/api/v1.0/tobs")

def tobs():
    """Return a list of temperatures for prior year"""
    # Query for the dates and temperature observations of the most active station for the previous year.
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
          
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(recent_date) - dt.timedelta(days=365)
    temperature = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.date > last_year)\
        .filter(Measurement.station=='USC00519281')\
        .order_by(Measurement.date).all()

# Create a list of dicts with `date` and `tobs` as the keys and values
    temperature_totals = []
    for x in temperature:
        row = {}
        row["date"] = temperature[0]
        row["tobs"] = temperature[1]
        temperature_totals.append(row)

    session.close()

    return jsonify(temperature_totals)  

    
    
 #################################################

@app.route("/api/v1.0/<start>")
def start():
# Create our session (link) from Python to the DB
    session = Session(engine)
# go back one year from start date and go to end of data for Min/Avg/Max temp   
    end_date= dt.datetime.strptime(start, '%Y-%m-%d')
    start_date = end_date - dt.timedelta(days=366)
    
    
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    session.close()
    
    return jsonify(list(np.ravel(trip_data)))
    
     
 #################################################
@app.route("/api/v1.0/<start>/<end>")
def startend():
# Create our session (link) from Python to the DB
    session = Session(engine)

  # go back one year from start/end date and get Min/Avg/Max temp     
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
   
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
   
    session.close()
   
    return jsonify(list(np.ravel(trip_data)))

   
    
      


if __name__ == '__main__':
    app.run(debug=True)

