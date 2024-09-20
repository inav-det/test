import requests, os, csv
import pandas as pd
import pytz
import random
import numpy as np
from datetime import datetime, timedelta, timezone
def time_to_seconds(time_str):
    if pd.isna(time_str):
        return np.nan  # Return NaN for missing values
    if isinstance(time_str, str):
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s
    return np.nan  # Return NaN for non-string values

def gen_random_numbers_in_range(low, high, n):
    return random.sample(range(low, high), n)

def process_column(column):
    # Convert strings to numbers (use `errors='coerce'` to handle non-numeric strings)
    column_numeric = pd.to_numeric(column, errors='coerce')

    # Custom function to check if a value is a whole number
    def is_whole_number(x):
        if pd.isna(x):
            return False
        return isinstance(x, (int, np.int64)) or (isinstance(x, (float, np.float64)) and x.is_integer())

    # Apply the function to each element in the column
    return column_numeric.apply(is_whole_number)

df_csv = pd.read_csv('./inav/2024-09-17_to_2024-09-19/inav.csv')
df_csv['Trip No.'] = pd.to_numeric(df_csv['Trip No.'], errors='coerce')
df_csv[f'tripnum_is_whole'] = process_column(df_csv['Trip No.'])
df_csv['rounded'] = np.floor((df_csv['Trip No.']))
df_csv['mileage'] = pd.to_numeric(df_csv['mileage'], errors='coerce')
df_csv['durationInSec'] = df_csv['travelTime'].apply(time_to_seconds)
print(df_csv)

prev_date = None
index_array = []
empty_index_array = []
start_array = []
end_array = []
duration_array = []
mileage_array = []
timegaps = []
temp_start = []
temp_end = []
fit_trips = []
data_array = []
prev_plate = None
row_length = (len(df_csv))
for index, row in df_csv.iterrows():    
    print(f'Index : {index}')
    tripnum = row['Trip No.']
    is_whole = row['tripnum_is_whole']
    date = row['start_date']
    startTime = row['startTime']
    endTime = row['endTime']
    plate = row['plate_number']
    plate_null = pd.isnull(df_csv.loc[index, 'plate_number'])
    duration = row['durationInSec']
    mileage = row['mileage']
    start_null = pd.isnull(df_csv.loc[index, 'startTime'])
    end_null = pd.isnull(df_csv.loc[index, 'endTime'])

    if is_whole:
        continue

    if plate_null:
        average_duration = sum(duration_array)/len(duration_array)
        min_duration = average_duration - 300
        max_duration = average_duration + 300

        for y in range(len(end_array)-1):
            end = datetime.strptime(end_array[y], '%H:%M:%S')
            start = datetime.strptime(start_array[y+1], '%H:%M:%S')
            timeInSec = (start - end).total_seconds()
            print(f'{timeInSec}')
            timegaps.append(timeInSec)
            if (max_duration/timeInSec) > 1.5:
                temp_start.append(end)
                temp_end.append(start)
                fit_trips.append(max_duration/timeInSec)

        for trips in range(len(fit_trips)):
            numberOfTrips = round(fit_trips[trips])
            count = 0
            initial = temp_start[trips]
            timePertrip = ((temp_end[trips] - temp_start[trips]).total_seconds())/numberOfTrips
            while count < numberOfTrips:  
                loop = 0
                while loop == 0:
                    departure = np.random.randint(120,300)
                    rand_duration = np.random.randint(min_duration, max_duration)
                    startTime = initial + timedelta(seconds=departure)
                    total_added = departure + rand_duration
                    if total_added <= timePertrip:
                        temp_time = startTime + timedelta(seconds=rand_duration)
                        count += 1
                        data = {
                            'startTime': startTime,
                            'endTime': temp_time,
                            'travelTime': rand_duration
                        }
                        data_array.append(data)
                        loop = 1
                        # print(data_array)

        for x in empty_index_array: 
            print("TERMINAL 2")
            rand_duration = np.random.randint(min_duration, max_duration)

            # hours = rand_duration // 3600
            # minutes = (rand_duration % 3600) // 60
            # seconds = rand_duration % 60
            # totalTravel = f'{hours:02}:{minutes:02}:{seconds:02}'

            # df_csv.loc[x, 'travelTime'] = totalTravel
            # print(rand_duration)
                    
            min_mileage = min(mileage_array)
            max_mileage = max(mileage_array)
            if min_mileage == max_mileage:
                min_mileage = min_mileage - 0.5
                max_mileage = max_mileage + 0.5
            rand_mileage = round(np.random.uniform(min_mileage, max_mileage),2)
            print(rand_mileage)

            df_csv.loc[x, 'mileage'] = rand_mileage
    
    if (prev_date == None or prev_date == date) and (prev_plate is None or prev_plate == plate) :
        if not start_null and not end_null:
            start_array.append(startTime)
            end_array.append(endTime)
            index_array.append(index)
            duration_array.append(duration)
            mileage_array.append(mileage)
        else:
            empty_index_array.append(index)
    else:
        start_array =[]
        end_array = []
        index_array =[]
        empty_index_array = []
        duration_array = []
        mileage_array = []    
        if not start_null and not end_null:
            start_array.append(startTime)
            end_array.append(endTime)
            index_array.append(index)
            duration_array.append(duration)
            mileage_array.append(mileage)
        else:
            empty_index_array.append(index)


    print(f'Start: {start_array}')
    print(f'End: {end_array}')
    print(f'With Values: {index_array}')
    print(f'Empty: {empty_index_array}')
    print(f'Mileage: {mileage_array}')

    prev_date = date
    prev_plate = plate

    if not empty_index_array:
        print('Trip Complete')
    else:
        print(f'Trip Incomplete for {date}')
    
    

    
        

