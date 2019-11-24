# Google Calendars Scraper and Visualization Tool
Note: Compatible with python3+ only.
## Scraper Instructions:
1.    Visit https://developers.google.com/calendar/quickstart/python, follow the instructions in step 1 and download credentials.json file into  the scraper's working directory. Follow step 2 to download google client library.
2.    Visit https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/ (Mac) or https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/(Windows)
to install MongoDB.
4. Install pymongo client for python 
* sudo easy_install pymongo
* sudo pip install --upgrade google-api-python-client
* sudo pip install google-auth-oauthlib
* sudo pip install click
5. Install click library for python
* pip install click
3. Open a terminal instance with no arguments to simply get results (python3 main.py).
4. You can also specify the following arguments while running the program
* --database=<database_name> (To insert the results into a database)
* --inputids=True/False (When set to true, the user is propted to enter which calendars the user wants results from Default:False)
* Eg. python scraper.py --database=caldb --sortbyeventsr=endTime --inputids=True
6.    Prints out events for each calendar in the format {
name: 
date: <datetime, day>
startTime: <datetime, time-of-day>
endTime: <datetime, time-of-day>
participants: [ <list of strings (invited members)> ]
length: <int, total event length in minutes>
} 
and inserts into database if specified.


## Visulalization Tool Instructions:
1.    Assumptions – The Database you  created using the scraper is named ‘caldb’.
2.    Install Flask using pip install Flask
3.    Navigate to the visualizer's directory and run ‘python3 visualize.py’ on a terminal window.
4.    Navigate to localhost:8000 on your web browser. The app is run there.
5.    Navigate to visualizer and select whether to displat time spent by each calendar, event, or participant.
6. Select any property to sort on and Ascending/Descending from dropdowns and click button to sort.

## Resources Used:

1. http://adilmoujahid.com/posts/2015/01/interactive-data-visualization-d3-dc-python-mongodb/
2. https://pythonspot.com/flask-and-great-looking-charts-using-chart-js/
3. https://www.patricksoftwareblog.com/creating-charts-with-chart-js-in-a-flask-application/
4. https://gitlab.com/patkennedy79/flask_chartjs_example/tree/master
5. https://developers.google.com/calendar/quickstart/python
6. https://kite.com/python/examples/5639/datetime-get-the-year,-month,-and-day-of-a-%60datetime%60
7. https://developers.google.com/gmail/markup/reference/datetime-formatting
8. https://stackoverflow.com/questions/24096409/how-to-format-the-output-of-a-datetime-event-of-a-google-calendar
9. https://www.w3schools.com/python/python_mongodb_getstarted.asp
