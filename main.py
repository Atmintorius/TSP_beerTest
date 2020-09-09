import time
start_time = time.time()
import sqlite3
from haversine import haversine, Unit
import math
import numpy as np

visitedBreweries = [0]
routeDistances = [0]
visitedCoordinates = [[0.000000, 0.000000]]

x = input('Press "d" to use default location (51.355468, 11.100790) or press "c" for custtom location. Then press Enter to proceed.\n')
if x == 'd':
    homeLocation = (51.355468, 11.100790)
    start_time = time.time()
    print("\nCalculations are running... Please wait.")
elif x == 'c':
    lat_str = input('Enter Latitude and Press Enter. Use dot (.) instead comma (,) for real numbers:\n')
    lat_float = float(lat_str)
    lon_str = input('Enter Longintude and Press Enter. Use dot (.) instead comma (,) for real numbers:\n')
    lon_float = float(lon_str)
    homeLocation = (lat_float, lon_float)
    start_time = time.time()
    print("\nCalculations are running... Please wait.")

def connectSQLite():
    sqliteConnection = sqlite3.connect(r'beerData\SQLite\beerData.db')
    cursor = sqliteConnection.cursor()

    sqlite_select_query = """SELECT brewery_id, latitude, longitude FROM geocodes"""
    cursor.execute(sqlite_select_query)
    records = cursor.fetchall()

    return records

def round_half_up(n, decimals = 0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier

def findIndex(theList, element):
    check = element
    index = ["{0}".format(index1) for index1,value1 in enumerate(theList) for index2,value2 in enumerate(value1) if value2==check]
    return int(index[0])

def findMinDistance (curLocation):
    minDistance = 2000

    records = connectSQLite()
    recordsList = np.array((records))

    for row in recordsList:
        for i in visitedBreweries:
            if int(row[0]) == int(i):
                index = findIndex(recordsList, row[0])
                recordsList[index][0] = 0
                break

    for row in recordsList:
        if int(row[0]) != 0:
            tryDestination = (float(row[1]), float(row[2]))
            distance = round_half_up(haversine(curLocation, tryDestination))
            if minDistance > distance and distance > 0:
                minDistance = distance
                brewery_index = row[0]
                newLocation = (float(row[1]), float(row[2]))
                newCoordinates = [float(row[1]), float(row[2])]

    visitedCoordinates.append(newCoordinates)
    visitedBreweries.append(int(brewery_index))
    routeDistances.append(int(minDistance))
    return int(minDistance), newLocation

def findShortestRoute():
    minDis, newLoc = findMinDistance(homeLocation)

    traveLeft = 2000 - minDis
    currentLocation = newLoc
    shortestReturn = 0

    while traveLeft >= shortestReturn:
        mDis, nLoc = findMinDistance(currentLocation)
        previousLocation = currentLocation
        currentLocation = nLoc
        traveLeft -= mDis
        shortestReturn = round_half_up(haversine(currentLocation, homeLocation))
        if traveLeft <= shortestReturn:
            del visitedBreweries[-1]
            del routeDistances[-1]
            del visitedCoordinates[-1]
            finalReturn = round_half_up(haversine(previousLocation, homeLocation))
            routeDistances.append(int(finalReturn))
            visitedCoordinates.append(homeLocation)

def showTravelRoute():
    count = 0
    findShortestRoute()
    print("Helicopter have visited ", len(visitedBreweries) - 1, " breweries:\n" )

    try:
        sqliteConnection = sqlite3.connect(r'beerData\SQLite\beerData.db')
        cursor = sqliteConnection.cursor()
        sql_select_breweries_query = """SELECT name FROM breweries WHERE id = ?"""

        for i in visitedBreweries:
            if i == 0:
                print("HOME : ", np.array(homeLocation)[0], np.array(homeLocation)[1], " distance ", routeDistances[0], "km")
                continue
            cursor.execute(sql_select_breweries_query, (i,))
            brew_records = cursor.fetchall()
            for row in brew_records:
                count += 1
                print("[", i, "]", row[0],": ", visitedCoordinates[count][0], visitedCoordinates[count][1], " distance ", routeDistances[count], "km")

        print("BACK HOME : ", np.array(homeLocation)[0], np.array(homeLocation)[1], " distance ", routeDistances[-1], "km\n")        
        print("Total distance travelled: ", sum(routeDistances), "km\n")

        cursor.close()
    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()

def showBeerTypes():
    findShortestRoute()
    beerTypes = []

    try:
        sqliteConnection = sqlite3.connect(r'beerData\SQLite\beerData.db')
        cursor = sqliteConnection.cursor()
        sql_select_beers_query ="""SELECT brewery_id, name FROM beers""" 
        
        cursor.execute(sql_select_beers_query)
        beer_records = cursor.fetchall()

        print("Collected beer types:")
        num = 0
        for i in visitedBreweries:
            for row in beer_records:
                if i == int(row[0]):
                    num += 1
                    print(num, ") ", row[1])
                    beerTypes.append(row[1])

        print("\nThere were collected", len(beerTypes), "beer types\n")

        cursor.close()
    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
    
if __name__ == '__main__':
    showTravelRoute()
    showBeerTypes()
    print("Calculations took: %s seconds" % (time.time() - start_time), "\n")