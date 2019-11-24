from __future__ import print_function
from datetime import datetime
import pymongo
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import click
import sys


class Calendar():

    def fetch_credentials(self):
        '''Fetches user credentials from tocken.pickle
        and credentials.json file.
        source of code:
        https://developers.google.com/calendar/quickstart/python
        '''

        # If modifying these scopes, delete the file token.pickle.
        # Scope for API calls
        # source:  https://developers.google.com/calendar/quickstart/python
        scopes = ['https://www.googleapis.com/auth/calendar.readonly']
        creds = None
        # The file token.pickle stores
        # the user's access and refresh tokens, and is
        # created automatically
        #  when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', scopes)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds

    def parse_data(self, service, id_list, idDict, inputids):
        '''Parses fetched data
        and inserts into id list based on whether the inputids
            argument is mentioned or not'''
        # For specifying a particular page in the calendar
        page_token = None
        counter = 0
        # Iterating over calendar entries
        while True:
            calendar_list = service.calendarList().list(
                pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                # Adding to ID list if inputids not specified
                if inputids == "False":
                    id_list.append(calendar_list_entry['id'])
                # Adding to ID dict if input ids is spfecified. ID List is
                # filled later
                elif inputids == "True":
                    print("Index#" + str(counter))
                    print(
                        calendar_list_entry.get(
                            'summary',
                            calendar_list_entry.get('id')))

                    idDict[str(counter)] = calendar_list_entry['id']
                    counter = counter + 1

            # Iterating to the next page
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

    def user_input(self, id_list, idDict):
        # Takes in input from user and fills in id list accordingly
        ids = input(
            "Enter calendar" +
            " index numbers displayed above ids (separate by whitespace): ")
        index_list = ids.split()
        for index in index_list:
            id_list.append(idDict.get(index))

    def populate_calendar_dict(self, id_list, service):

        cal_dict = {}
        # Get events for calenders spoecified
        print('Getting the events...')
        print('Required Calendar Entries - ')
        # Iterating over id lists
        for id in id_list:
            # Call the Calendar API
            # now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC
            # time
            events_result = service.events().list(calendarId=id).execute()

            # Get all the events for the current ID
            events = events_result.get('items', [])

            cal_dict[id] = []
            # Iterate over the calendar's events
            for event in events:
                '''
                temp dictionary for events with format - s
                {
                    name:
                    date: <datetime, day>
                    startTime: <datetime, time-of-day>
                    endTime: <datetime, time-of-day>
                    participants: [ <list of strings (invited members)> ]
                    length: <int, total event length in minutes>
                }
                '''
                temp = {}
                # Variable for the case no date is specified
                dtTemp = '2019-01-05T23:00:00+01:00'

                # Summary of event
                temp["name"] = event.get("summary", event.get("id"))

                # If start time is mentioned
                if "start" in event:
                    ''' Parses start and end times
                    from the string format
                    mentioned here -
                    https://developers.google.com/gmail/markup/reference/datetime-formatting
                    ,converts to dateTime object for computing length.
                     Separates into  date, time and day and
                    then converts to separated strings
                    to be inserted separately '''

                    # Date computation
                    dt = datetime.strptime(event["start"]
                                           .get('dateTime', dtTemp),
                                           "%Y-%m-%dT%H:%M:%S%z")
                    day = dt.day
                    # Inserted string instead of datetime object as mongodb
                    # can't parse datetime
                    tempList = [event["start"].get('dateTime', dtTemp), day]
                    temp["date"] = tempList

                    # Start Time Computation
                    dt2 = datetime.strptime(
                        event["start"].get(
                            'dateTime',
                            dtTemp),
                        "%Y-%m-%dT%H:%M:%S%z")
                    time = dt2.strftime("%H:%M:%S%z")
                    tempList2 = [event["start"].get('dateTime', dtTemp), time]
                    temp["startTime"] = tempList2

                    # End Time Computation
                    dt3 = datetime.strptime(
                        event["end"].get(
                            'dateTime',
                            dtTemp),
                        "%Y-%m-%dT%H:%M:%S%z")
                    time2 = dt3.strftime("%H:%M:%S%z")
                    tempList3 = [event["end"].get('dateTime', dtTemp), time2]
                    temp["endTime"] = tempList3
                # Inserting attendees in event dict
                temp["participants"] = []
                if "attendees" in event:
                    for attendee in event["attendees"]:
                        for attendee in event["attendees"]:
                            temp["participants"].append(attendee.get(
                                "displayName", attendee.get("email")))
                # Computes Total Length of event in minutes by dividing total
                # length in secs by 60
                length = (dt3 - dt2).total_seconds() / 60.0
                # Inserting length in event dict
                temp["length"] = length
                # Adds event to list of events coresponding to the calendar
                # entry
                cal_dict[id].append(temp)
        return cal_dict

    def insert_into_db(self, cal_dict, database):
        db_name = database

        # Set up Mongo Clients
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")

        # Set up Database (Name this Caldb if you want to use the visualisers)
        mydb = myclient[db_name]
        # Set up collection named 'Calendars'
        mycol = mydb["Calendars"]
        counter = 0
        for id, events in cal_dict.items():
            mydict = {}
            mydict["calendar_id"] = id
            mydict["_id"] = counter
            mydict["events"] = events
            # Insert into the Collection
            entry = mycol.insert_one(mydict)
            print(entry.inserted_id)
            counter += 1

    def print_dict(self, cal_dict):
        print(cal_dict)
        print("Run with option --help to learn about optional arguments")

    def run(
            self,
            database,
            inputids):
        """ Fetches, parses and stores user calendar data based on user input
        and inserts into MongoDB Database, if required
        """
        # If more than required arguments specified
        if(len(sys.argv) > 5):
            print("ERROR")
            return

        creds = self.fetch_credentials()

        # builds calender API call using credentials
        service = build('calendar', 'v3', credentials=creds)

        # Dictionary storing cal ids
        idDict = {}
        # List of user calendars.
        id_list = []

        # Parse the data
        self.parse_data(service, id_list, idDict, inputids)

        # If the user wants to input IDs
        if inputids == "True":
            self.user_input(id_list, idDict)

        # Populates dictionary containing the calendars and their entries
        cal_dict = self.populate_calendar_dict(id_list, service)

        # If database is specified insert create collection and insert
        if database != "False":
            self.insert_into_db(cal_dict, database)

        return cal_dict


@click.command()
@click.option('--database', default="False", help = "To insert the results into a database(Default:False). Use: --database=<database_name>/False ")
@click.option('--inputids', default="False", help ="When set to true, the user is propted to enter which calendars the user wants results from (Default:False). Use: --inputids=True/False")
def main(
        database,
        inputids):
    MyCalendar = Calendar()
    MyCalendar.print_dict(
        MyCalendar.run(
            database,
            inputids))

    if database != "False":
         print("Inserted into database " + database)



if __name__ == '__main__':
    main()
