# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, func, desc
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session 
import datetime as dt



#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine=create_engine(f'sqlite:///Resources/hawaii.sqlite')
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
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
def home():
    'homepage: lists all available routes'
    return (
        f"Welcome to Homepage,<br/"
        f"here are all the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/(start_date)**<br/>"
        f"/api/v1.0/(start date)/(end date)**<br/>"
        f"**start date: input a date between 2010-01-01 & 2017-08-23 in the format YYYY-MM-DD<br/>"
        f"**end date: input a date between (start date) & 2017-08-23 in the format YYY-MM-DD"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    "Precipitation of the latest year period"
    session=Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    recent_date = dt.datetime.strptime(recent_date,'%Y-%m-%d').date()
    one_year_ago = recent_date-dt.timedelta(days=365)
    latest_year = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago ).order_by(Measurement.date).all()
    session.close()

    data_list = [] 
    for date, prcp in latest_year: 
        data_dict = {} 
        data_dict['Date'] = date 
        data_dict['Precipitation'] = prcp 
        data_list.append(data_dict) 
    return (jsonify(data_list))



@app.route("/api/v1.0/stations")
def station():
    "Station database"
    session=Session(engine)
    station_list = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    session.close()

    data_list = [] 
    for station,name,latitude,longitude,elevation in station_list: 
        data_dict = {} 
        data_dict['Station'] = station 
        data_dict['Name'] = name 
        data_dict['Latitude'] = latitude
        data_dict['Longitude'] = longitude
        data_dict['Elevation'] = elevation
        data_list.append(data_dict)

    return jsonify(data_list)




@app.route("/api/v1.0/tobs")    
def tobs():
    "Temperature of the latest year period of the most active station"
    session=Session(engine)
    most_active_station = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = (dt.datetime.strptime(recent_date,'%Y-%m-%d')-dt.timedelta(days=365)).date()
    temp_station = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago ).filter(Measurement.station == f'{most_active_station[0][0]}').order_by(Measurement.date.asc()).all()
    session.close()

    data_list = [] 
    for date,tobs in temp_station: 
        data_dict = {} 
        data_dict['Date'] = date 
        data_dict['TOBS'] = tobs 
        data_list.append(data_dict) 
    return (jsonify(data_list))



@app.route("/api/v1.0/<start>")
def temperature_start(start):
    "the temperature status from the selected start date"
    try:
        start_date = dt.datetime.strptime(start,'%Y-%m-%d').date()
    except:
        return jsonify('Error: input date is not in correct format (YYYY-MM-DD)')
    
    session=Session(engine)
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_date = dt.datetime.strptime(latest_date,'%Y-%m-%d').date()
    earliest_date = session.query(Measurement.date).order_by(Measurement.date.asc()).first()[0]
    earliest_date = dt.datetime.strptime(earliest_date,'%Y-%m-%d').date()

    if not (earliest_date <= start_date <= latest_date):
        return(f"Error: input date is not within rage ({earliest_date} to {latest_date})")

    temp = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).group_by(Measurement.date).all()
    session.close()

    data_list = [] 
    for date,min,max,avg in temp: 
        data_dict = {} 
        data_dict['Date'] = date 
        data_dict['TMIN'] = min 
        data_dict['TMAX'] = max 
        data_dict['TAVG'] = avg 
        data_list.append(data_dict) 
    return (jsonify(data_list))



@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end(start,end):
    "the temperature status from the selected start to end date"
    try:
        start_date = dt.datetime.strptime(start,'%Y-%m-%d').date()
    except:
        return jsonify('Error: start date is not in correct format (YYYY-MM-DD)')
    try:
        end_date = dt.datetime.strptime(end,'%Y-%m-%d').date()
    except:
        return jsonify('Error: end date is not in correct format (YYYY-MM-DD)')
    
    session=Session(engine)
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latest_date = dt.datetime.strptime(latest_date,'%Y-%m-%d').date()
    earliest_date = session.query(Measurement.date).order_by(Measurement.date.asc()).first()[0]
    earliest_date = dt.datetime.strptime(earliest_date,'%Y-%m-%d').date()

    if not (earliest_date <= start_date <= latest_date):
        return(f"Error: start date is out of rage, please select ({earliest_date} to {end_date})")
    if not (start_date <= end_date <= latest_date):
        return(f"Error: end date is out of rage, please select ({start_date} to {latest_date})")

    temp = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).group_by(Measurement.date).all()
    session.close()

    data_list = [] 
    for date,min,max,avg in temp: 
        data_dict = {} 
        data_dict['Date'] = date 
        data_dict['TMIN'] = min 
        data_dict['TMAX'] = max 
        data_dict['TAVG'] = avg 
        data_list.append(data_dict) 
    return (jsonify(data_list))



if __name__ == "__main__":
    app.run(debug=True)