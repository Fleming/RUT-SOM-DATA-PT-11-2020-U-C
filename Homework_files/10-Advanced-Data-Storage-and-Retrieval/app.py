{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 16,
   "metadata": {},
   "outputs": [],
   "source": [
    "from flask import Flask, jsonify\n",
    "import numpy as np\n",
    "from datetime import datetime\n",
    "import datetime as dt\n",
    "from dateutil.relativedelta import relativedelta"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "metadata": {},
   "outputs": [],
   "source": [
    "import sqlalchemy\n",
    "from sqlalchemy.ext.automap import automap_base\n",
    "from sqlalchemy.orm import Session\n",
    "from sqlalchemy import create_engine, func"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "metadata": {},
   "outputs": [],
   "source": [
    "#################################################\n",
    "# Database Setup\n",
    "#################################################\n",
    "engine = create_engine(\"sqlite:///Resources/hawaii.sqlite\")\n",
    "\n",
    "# reflect an existing database into a new model\n",
    "Base = automap_base()\n",
    "# reflect the tables\n",
    "Base.prepare(engine, reflect=True)\n",
    "\n",
    "# We can view all of the classes that automap found\n",
    "#Base.classes.keys()\n",
    "\n",
    "# Save reference to the tables\n",
    "Measurement = Base.classes.measurement\n",
    "Station = Base.classes.station"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "metadata": {},
   "outputs": [],
   "source": [
    "#################################################\n",
    "# Flask Setup\n",
    "#################################################\n",
    "app = Flask(__name__)\n",
    "\n",
    "\n",
    "#################################################\n",
    "# Flask Routes\n",
    "#################################################\n",
    "\n",
    "@app.route(\"/\")\n",
    "def welcome():\n",
    "    \"\"\"List all available api routes.\"\"\"\n",
    "    return (\n",
    "        f\"Welcome to the Climate App API!<br>\"\n",
    "        f\"Available Routes:<br/>\"\n",
    "        f\"/api/v1.0/precipitation<br/>\"\n",
    "        f\"/api/v1.0/stations<br/>\"\n",
    "        f\"/api/v1.0/tobs<br/>\"\n",
    "        f\"/api/v1.0/start<br/>\"\n",
    "        f\"/api/v1.0/start/end<br/>\"\n",
    "    )\n",
    "\n",
    "@app.route(\"/api/v1.0/precipitation\")\n",
    "def precipitation():\n",
    "    # Create our session (link) from Python to the DB\n",
    "    session = Session(engine)\n",
    "\n",
    "    \"\"\"Return a list of precipitation amounts\"\"\"\n",
    "    # Query all precipitation amounts\n",
    "    #rainfall = session.query(Measurement.date, Measurement.prcp).filter(func.strftime(\"%y-%m-%d\", Measurement.date == date).all()\n",
    "    last_measurement_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()\n",
    "     \n",
    "    latest_date = last_measurement_data_point [0]\n",
    "    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')\n",
    "    latest_date = latest_date.date()\n",
    "    date_year_ago = latest_date - relativedelta(years=1)\n",
    "\n",
    "    # Perform a query to retrieve the data and precipitation scores.\n",
    "    last_year_data = session.query(Measurement.date, Measurement.prcp).filter(\n",
    "        Measurement.date >= date_year_ago).all()\n",
    "    session.close()\n",
    "\n",
    " # Create a dictionary from the row data and append to a list of dates and precipitation\n",
    "    all_precipitation = []\n",
    "    for date, prcp in last_year_data:\n",
    "        if prcp != None:\n",
    "            precip_dict = {}\n",
    "            precip_dict[date] = prcp\n",
    "            all_precipitation.append(precip_dict)\n",
    "\n",
    "    return jsonify(all_precipitation)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/tobs\")\n",
    "def tobs():\n",
    "    \"\"\"Query for the dates and temperature observations from a year from the last data point for the most active station.\"\"\"\n",
    "    # Create our session (link) from Python to the DB.\n",
    "    session = Session(engine)\n",
    "\n",
    "    # Calculate the date 1 year ago from the last data point in the database.\n",
    "    temp_observation = session.query(\n",
    "        Measurement.date).order_by(Measurement.date.desc()).first()\n",
    "    \n",
    "    latest_date = temp_observation [0]\n",
    "    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')\n",
    "    latest_date = latest_date.date()\n",
    "    date_year_ago = latest_date - relativedelta(years=1)\n",
    "\n",
    "    # Find the most active station.\n",
    "    most_active_station = session.query(Measurement.station).\\\n",
    "        group_by(Measurement.station).\\\n",
    "        order_by(func.count().desc()).\\\n",
    "        first()\n",
    "\n",
    "    # Get the station id of the most active station.\n",
    "    most_active_station_id = most_active_station [0]\n",
    "    print(f\"The station id of the most active station is {most_active_station_id}.\")\n",
    "\n",
    "    # Perform a query to retrieve the data and temperature scores for the most active station from the last year.\n",
    "    data_from_last_year = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station_id).filter(Measurement.date >= date_year_ago).all()\n",
    "\n",
    "    session.close()\n",
    "\n",
    "    # Convert the query results to a dictionary using date as the key and temperature as the value.\n",
    "    all_temperatures = []\n",
    "    for date, temp in data_from_last_year:\n",
    "        if temp != None:\n",
    "            temp_dict = {}\n",
    "            temp_dict[date] = temp\n",
    "            all_temperatures.append(temp_dict)\n",
    "    # Return the JSON representation of dictionary.\n",
    "    return jsonify(all_temperatures)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/stations\")\n",
    "def stations():\n",
    "    \"\"\"Return a JSON list of stations from the dataset.\"\"\"\n",
    "    # Create our session (link) from Python to the DB\n",
    "    session = Session(engine)\n",
    "\n",
    "    # Query for stations.\n",
    "    stations = session.query(Station.station, Station.name,\n",
    "                             Station.latitude, Station.longitude, Station.elevation).all()\n",
    "\n",
    "    session.close()\n",
    "\n",
    "    # Convert the query results to a dictionary.\n",
    "    all_stations = []\n",
    "    for station, name, latitude, longitude, elevation in stations:\n",
    "        station_dict = {}\n",
    "        station_dict[\"station\"] = station\n",
    "        station_dict[\"name\"] = name\n",
    "        station_dict[\"latitude\"] = latitude\n",
    "        station_dict[\"longitude\"] = longitude\n",
    "        station_dict[\"elevation\"] = elevation\n",
    "        all_stations.append(station_dict)\n",
    "\n",
    "    # Return the JSON representation of dictionary.\n",
    "    return jsonify(all_stations)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null;
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route('/api/v1.0/<start>', defaults={'end': None})\n",
    "@app.route(\"/api/v1.0/<start>/<end>\")\n",
    "def determine_temps_for_date_range(start, end):\n",
    "    \"\"\"Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.\"\"\"\n",
    "    \"\"\"When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.\"\"\"\n",
    "    \"\"\"When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.\"\"\"\n",
    "    # Create our session (link) from Python to the DB.\n",
    "    session = Session(engine)\n",
    "\n",
    "    # If we have both a start date and an end date.\n",
    "    if end != None:\n",
    "        temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\\\n",
    "            filter(Measurement.date >= start).filter(\n",
    "            Measurement.date <= end).all()\n",
    "    # If we only have a start date.\n",
    "    else:\n",
    "        temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\\\n",
    "            filter(Measurement.date >= start).all()\n",
    "\n",
    "    session.close()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      " * Serving Flask app \"__main__\" (lazy loading)\n",
      " * Environment: production\n",
      "   WARNING: This is a development server. Do not use it in a production deployment.\n",
      "   Use a production WSGI server instead.\n",
      " * Debug mode: on\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      " * Restarting with stat\n"
     ]
    },
    {
     "ename": "SystemExit",
     "evalue": "1",
     "output_type": "error",
     "traceback": [
      "An exception has occurred, use %tb to see the full traceback.\n",
      "\u001b[1;31mSystemExit\u001b[0m\u001b[1;31m:\u001b[0m 1\n"
     ]
    }
   ],
   "source": [
    "    # Convert the query results to a list.\n",
    "    temperature_list = []\n",
    "    no_temperature_data = False\n",
    "    for min_temp, avg_temp, max_temp in temperature_data:\n",
    "        if min_temp == None or avg_temp == None or max_temp == None:\n",
    "            no_temperature_data = True\n",
    "        temperature_list.append(min_temp)\n",
    "        temperature_list.append(avg_temp)\n",
    "        temperature_list.append(max_temp)\n",
    "    # Return the JSON representation of dictionary.\n",
    "    if no_temperature_data == True:\n",
    "        return f\"No temperature data found for the given date range. Try another date range.\"\n",
    "    else:\n",
    "        return jsonify(temperature_list)\n",
    "\n",
    "\n",
    "if __name__ == '__main__':\n",
    "    app.run(debug=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.1"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
