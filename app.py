import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)
app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start_date><br/>"
        f"/api/v1.0/<start_date>/<end_date><br/>")

@app.route("/api/v1.0/precipitation")
def precipitation():
    precipitation_data = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()

    total_precipitation=[]
    for precipitation in precipitation_data:
        precip_dict = {}
        precip_dict["date"] = precipitation.date
        precip_dict["prcp"] = precipitation.prcp
        total_precipitation.append(precip_dict)

    return jsonify(total_precipitation)
    
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Measurement.station, func.count(Measurement.station)).\
                group_by(Measurement.station).\
                order_by(func.count(Measurement.station).desc()).all()

    stations_list = []
    for station in stations:
        station_dict = {}
        station_dict["station"] = station[0]
        station_dict["count"] = station[1]
        stations_list.append(station_dict)

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    for date in last_date:
        split_last_date = date.split('-')
    
    last_year = int(split_last_date[0])
    last_month = int(split_last_date[1])
    last_day = int(split_last_date[2])
    
    query_date = dt.date(last_year, last_month, last_day) - dt.timedelta(days=365)
    
   
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>=query_date).order_by(Measurement.date).all()

    pastYear_tobs=[]
    for tobs_row in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = tobs_row.date
        tobs_dict["station"] = tobs_row.tobs
        pastYear_tobs.append(tobs_dict)

    return jsonify(pastYear_tobs)

@app.route("/api/v1.0/<start_date>")
def calc_temps_start(start_date):
    
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= "2012-02-08").all()

    calc_tobs=[]
    for row in results:
        calc_tobs_dict = {}
        calc_tobs_dict["TMIN"] = row[0]
        calc_tobs_dict["TAVG"] = row[1]
        calc_tobs_dict["TMAX"] = row[2]
        calc_tobs.append(calc_tobs_dict)

    return jsonify(calc_tobs)

@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps_start_end(start_date, end_date):

    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= "2012-02-08").filter(Measurement.date <= "2012-03-05").all()
    
    calc_tobs=[]
    for row in results:
        calc_tobs_dict = {}
        calc_tobs_dict["TMIN"] = row[0]
        calc_tobs_dict["TAVG"] = row[1]
        calc_tobs_dict["TMAX"] = row[2]
        calc_tobs.append(calc_tobs_dict)

    return jsonify(calc_tobs)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)