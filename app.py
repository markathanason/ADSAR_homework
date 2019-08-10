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
        f"/api/v1.0/start_date (average only)<br/>"
        f"/api/v1.0/start_date/end_date (average only)<br/>")

@app.route("/api/v1.0/precipitation")
def precipitation():
    precipitation_data = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()
    total_precipitation=[]
    for date, prcp in precipitation_data:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        total_precipitation.append(precipitation_dict)
    session.close()
    return jsonify(total_precipitation)
    
@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    stations_list = []
    for station, count in stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["ID"] = count
        stations_list.append(station_dict)
    session.close()
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
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= query_date).order_by(Measurement.date).all()

    pastYear_tobs=[]
    for date, station in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["station"] = station
        pastYear_tobs.append(tobs_dict)
        session.close()
    return jsonify(pastYear_tobs)

@app.route("/api/v1.0/<start_date>")
def calc_temps_start(start_date):
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    calc_tobs=[]
    for TMIN, TAVG, TMAX in temps:
        calc_tobs_dict = {}
        calc_tobs_dict["TMIN"] = TMAX
        calc_tobs_dict["TAVG"] = TAVG
        calc_tobs_dict["TMAX"] = TMIN
        calc_tobs.append(calc_tobs_dict)
    session.close()
    return jsonify(calc_tobs)

@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps_start_end(start_date, end_date):
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    calc_tobs=[]
    for TMIN, TAVG, TMAX in temps:
        calc_tobs_dict = {}
        calc_tobs_dict["TMIN"] = TMAX
        calc_tobs_dict["TAVG"] = TAVG
        calc_tobs_dict["TMAX"] = TMIN
        calc_tobs.append(calc_tobs_dict)
    session.close()
    return jsonify(calc_tobs)

if __name__ == '__main__':
    app.run(debug=True)