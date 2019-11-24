import pymongo
from flask import Flask
from flask import render_template
from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps
import operator
import flask

''' Sources of Code -
https://www.patricksoftwareblog.com/creating-charts-with-chart-js-in-a-flask-application/
, https://pythonspot.com/flask-and-great-looking-charts-using-chart-js/'''
app = Flask(__name__)
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DBS_NAME = 'caldb'
COLLECTION_NAME = 'Calendars'
FIELDS = {'calendar_id': True, 'events': True, '_id': False}


def connect():
    # Starts connection to mongoDB server
    return MongoClient(MONGODB_HOST, MONGODB_PORT)


def get_collection(connection):
    # Fetches the collection
    return connection[DBS_NAME][COLLECTION_NAME]


def get_calendars(collection):
    # Projects the collection using a projection query
    return collection.find(projection=FIELDS)


def sorter(lengthDict, key_dict, reverseBool, sort_type):
    legend = "Total time spent on event (in minutes)"
    sorted_dict = {}
    for key, value in sorted(key_dict.items(), key=lambda item: item[1], reverse = reverseBool):
        sorted_dict[key] = value
        
    labels = []
    values = []
    for key in sorted_dict.keys():
        labels.append(key)
        #sorted_dict[key] = lengthDict[key]
        values.append(lengthDict[key])

    return render_template('chart.html', values=values,labels=labels, legend=legend, xType = "Events", renderGraph = "True", sorted = "True", reverse = str(reverseBool), prev_type = sort_type)



@app.route("/", methods=['GET', 'POST'])
def visualise():

    if flask.request.method == 'POST':
        if flask.request.form.get("xAxis") == "Events" or flask.request.form.get("XAxisVar") == "Events":
            return visualiseByEvents()
        elif flask.request.form.get("xAxis") == "Calendars" or flask.request.form.get("XAxisVar") == "Calendars":
            return visualiseByCalendar()
        elif flask.request.form.get("xAxis") == "Participants" or flask.request.form.get("XAxisVar") == "Participants":
            return visualisebyAttendees()

    elif flask.request.method == 'GET':
        return render_template('chart.html', renderGraph = "False", sorted = "False", prev_type = " ", xType = " ")




def visualiseByEvents():
    connection = connect()
    calendars = get_calendars(get_collection(connection))
    labels = []
    values = []
    legend = "Time spent on event"
    lengthDict = {}
    date_dict = {}
    sTime_dict = {}
    eTime_dict = {}
    participants_dict = {}

    # Append events to x axis labels and time spent per each to y axis
    for calendar in calendars:
        for event in calendar.get("events"):
            dtTemp = '2019-01-05T23:00:00+01:00'
            dateTemp = '2019-01-05T23:00:00+01:00'
            labels.append(event.get("name"))
            values.append(event.get("length"))
            lengthDict[event.get("name")] = event.get("length")
            if event.get("startTime"):
                sTime_dict[event.get("name")] = event.get("startTime")[0]
            else:
                sTime_dict[event.get("name")] = dtTemp
            
            if event.get("endTime"):
                eTime_dict[event.get("name")] = event.get("endTime")[0]
            else:
                eTime_dict[event.get("name")] = dtTemp
            if event.get("date"):
                date_dict[event.get("name")] = event.get("date")[0]
            else:
                date_dict[event.get("name")] = dateTemp
            participants_dict[event.get("name")] = len(event.get("participants"))


    if flask.request.form.get("type") == "LENGTH" and flask.request.form.get("type2") == "ASC":
        sorted_dict = {}
        for key, value in sorted(lengthDict.items(), key=lambda item: item[1]):
            sorted_dict[key] = value
        connection.close()
        return render_template('chart.html', values=sorted_dict.values(),
                labels=sorted_dict.keys(), legend=legend, xType = "Events", renderGraph = "True", sorted = "True", prev_selected = "Events", reverse = "False", prev_type = "LENGTH")
    
    elif flask.request.form.get("type") == "LENGTH" and flask.request.form.get("type2") == "DESC":
        sorted_dict = {}
        for key, value in sorted(lengthDict.items(), key=lambda item: item[1], reverse=True):
            sorted_dict[key] = value
        connection.close()
        return render_template('chart.html', values=sorted_dict.values(),
                labels=sorted_dict.keys(), legend=legend, xType = "Events", renderGraph = "True", sorted = "True", prev_selected = "Events", reverse = "True", prev_type = "LENGTH")

    elif flask.request.form.get("type") == "DATE":
        if flask.request.form.get("type2") == "ASC":
            return sorter(lengthDict,date_dict,False, "DATE")
        elif flask.request.form.get("type2") == "DESC":
            return sorter(lengthDict,date_dict,True, "DATE")

    elif flask.request.form.get("type") == "STARTTIME":
        if flask.request.form.get("type2") == "ASC":
            return sorter(lengthDict,sTime_dict,False, "STARTTIME")
        elif flask.request.form.get("type2") ==  "DESC":
            return sorter(lengthDict,sTime_dict,True, "STARTTIME")

    elif flask.request.form.get("type") == "ENDTIME":
        if flask.request.form.get("type2") == "ASC":
            return sorter(lengthDict,eTime_dict,False, "ENDTIME")
        elif flask.request.form.get("type2") ==  "DESC":
            return sorter(lengthDict,eTime_dict,True, "ENDTIME")

    elif flask.request.form.get("type") == "P":
        if flask.request.form.get("type2") == "ASC":
            return sorter(lengthDict,participants_dict,False, "P")
        elif flask.request.form.get("type2") == "DESC":
            return sorter(lengthDict,participants_dict,True, "P")
    connection.close()
    # Render the html template
    return render_template('chart.html', values=values,
                           labels=labels, legend=legend, xType = "Events", renderGraph = "True", sorted = "False", prev_selected = "Events")


def visualiseByCalendar():
    calendars = []
    connection = connect()
    prev_type = " "
    reverse = "False"
    if flask.request.method == 'POST':
        if flask.request.form.get("type") == "ID" and flask.request.form.get("type2") == "ASC":
            prev_type = "ID"
            calendars = get_calendars(get_collection(connection)).sort("calendar_id", pymongo.ASCENDING)
        elif flask.request.form.get("type") == "ID" and flask.request.form.get("type2") == "DESC":
            calendars = get_calendars(get_collection(connection)).sort("calendar_id", pymongo.DESCENDING)
            prev_type = "ID"
            reverse = "True"
        else:
            calendars = get_calendars(get_collection(connection))
    elif flask.request.method == 'GET':
        calendars = get_calendars(get_collection(connection))
    
    labels = []
    values = []
    legend = "Total Time spent on calendar (in minutes)"
    lengthDict = {}
    # Append Calendars to x axis labels and time spent per each calendar to y
    # axis
    for calendar in calendars:
        labels.append(calendar.get("calendar_id"))
        totalLength = 0.0
        for event in calendar.get("events"):
            totalLength += event.get("length")
        values.append(totalLength)
        lengthDict[calendar.get("calendar_id")] = totalLength
    if flask.request.form.get("type") == "LENGTH" and   flask.request.form.get("type2") == "ASC":
        prev_type = "LENGTH"
        sorted_d = {}
        for key, value in sorted(lengthDict.items(), key=lambda item: item[1]):
            sorted_d[key] = value
        connection.close()
        return render_template('chart.html', values=sorted_d.values(),
                    labels=sorted_d.keys(), legend=legend, xType = "Calendars", renderGraph = "True", sorted = "True", prev_selected = "Calendars", reverse = "False", prev_type = prev_type)
    if flask.request.form.get("type") == "LENGTH" and   flask.request.form.get("type2") == "DESC":
        prev_type = "LENGTH"
        sorted_d = {}
        for key, value in sorted(lengthDict.items(), key=lambda item: item[1], reverse=True):
            sorted_d[key] = value
        connection.close()
        return render_template('chart.html', values=sorted_d.values(),
                    labels=sorted_d.keys(), legend=legend, xType = "Calendars", renderGraph = "True", sorted = "True", prev_selected = "Calendars", reverse = "True", prev_type = prev_type)
            
    connection.close()
    # Render the html template
    return render_template('chart.html', values=values,
                        labels=labels, legend=legend, xType = "Calendars", renderGraph = "True", sorted = "False", prev_selected = "Calendars", prev_type = prev_type, reverse = reverse)



def visualisebyAttendees():
    connection = connect()
    calendars = get_calendars(get_collection(connection))
    labels = []
    values = []
    partdict = {}
    legend = "Total time spent by participant (in minutes)"

    for calendar in calendars:  # For each calendar
        for event in calendar.get("events"):  # For each event on this calendar
            # Sum up the time spent with each participant
            for participant in event.get("participants"):
                if participant not in partdict:
                    partdict[participant] = event.get("length")
                else:
                    partdict[participant] += event.get("length")

    # Append each attendee throughout all calendars to x axis labels and time
    # spent per each to y axis

    prev_selected = "Calendars"
    sorted_var = "False"
    reverse_var = "True"
    prev_type = " "

    if flask.request.form.get("type") == "NAME":
        prev_type = "NAME"
        if flask.request.form.get("type2") == "ASC":
            for key in sorted(partdict.keys()):
                labels.append(key)
                values.append(partdict[key])
                reverse_var = "False"
        elif flask.request.form.get("type2") == "DESC":
            for key in sorted(partdict.keys(), reverse = True):
                labels.append(key)
                values.append(partdict[key])
        sorted_var = "True"

    elif flask.request.form.get("type") == "LENGTH":
        prev_type = "LENGTH"
        if flask.request.form.get("type2") == "ASC":
            for key, value in sorted(partdict.items(), key=lambda item: item[1]):
                labels.append(key)
                values.append(value)
                reverse_var = "False"
        elif flask.request.form.get("type2") == "DESC":
            for key, value in sorted(partdict.items(), key=lambda item: item[1], reverse=True):
                labels.append(key)
                values.append(value)
                
        sorted_var = "True"

    else:
        for participant, time in partdict.items():
            labels.append(participant)
            values.append(time)
    connection.close()
    # Render the html template
    return render_template('chart.html', values=values,
                           labels=labels, legend=legend, xType = "Participants", renderGraph = "True", sorted = sorted_var, prev_selected = prev_selected, reverse = reverse_var, prev_type = prev_type)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
