# -*- coding: utf-8 -*-



#SETTINGS
#
# Be sure to include the file extensions in the file names.
Year = "2017"
#This is the year you are wanting to compare Google's Location History to Mile IQ for.
Google_Location_History_Filename = "LocationHistory.json"
MileIQ_Filename = '2017/MileIQ_2017.csv'
#This is the report available from https://dashboard.mileiq.com/reports
#Be sure to select the
#
Output_Filename = str(Year)+ "MissingDays.csv"














import sys
from datetime import datetime
import ijson
import csv
import arrow





def create_feature(obj):
    return datetime.fromtimestamp(int(obj['timestampMs']) / 1000.0).date().isoformat()



def parse_location(stream):
    parser = ijson.parse(stream)
    reading = False
    obj = {}
    key = None
    value = None
    for prefix, event, value in parser:
        if prefix == 'locations' and event == 'start_array':
            reading = True
        elif prefix == 'locations' and event == 'end_array':
            reading = False
        elif reading:
            if event == 'start_map' and prefix == 'locations.item':
                obj = {}
            elif event == 'end_map' and prefix == 'locations.item':
                yield create_feature(obj)
            elif event == 'map_key':
                key = value
            elif prefix == 'locations.item.%s' % key and value is not None:
                obj[key] = value


if __name__ == '__main__':

    MIQdates = set()
    with open(MileIQ_Filename) as tmp:
        for i in range(1,13):
            next(tmp, None)

        reader = (csv.DictReader(tmp))

        for row in reader:
            stamp = row["START_DATE*"]
            if stamp == "Totals":
                print("I reached the totals section, stopping reader.")
                break
            date=arrow.get(stamp,["MM/DD/YYYY HH:mm",
                                  "M/DD/YYYY HH:mm",
                                  "M/DD/YYYY H:mm",
                                  "MM/D/YYYY HH:mm",
                                  "MM/D/YYYY H:mm",
                                  "M/D/YYYY H:mm"]).date().isoformat()

            #print (date)

            MIQdates.add(date)


    GLHdates = set()
    current = 0
    with open(Google_Location_History_Filename, 'r') as file:
        for date in parse_location(file):
            print("This is the day im working on ", date)
            if date[0:4] == Year:
                GLHdates.add(date)
            else:
                print("Year was ",date[0:4]," ended Google Location History reading...")
                break
            current = current+1

            print (current, "data points analyzed...\n")


    missing = GLHdates - MIQdates
    missinglist = []
    for m in missing:
        missinglist.append(m)
    missinglist.sort()
    print("Missing Days:")
    for m in missinglist:
        print(m)

    with open(Output_Filename, 'w') as output:
        writer = csv.writer(output, quotechar='|',quoting=csv.QUOTE_MINIMAL)
        writer.writerow("Date")
        for m in missinglist:
            writer.writerow(m)

    print("Missing days have been written to a CSV file named: "+str(Output_Filename))