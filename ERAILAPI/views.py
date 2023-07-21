import pandas as pd
from datetime import datetime, timedelta
import json
from django.http import JsonResponse
from .serializers import TraiSerializers
from rest_framework.response import Response


minutes = 4 #min
between_minutes = 60 #min

current_time = datetime.now()
increment = timedelta(minutes=minutes)
range = timedelta(minutes=between_minutes)

new_time = current_time + increment
new_time = new_time.time()

range_time = current_time + range
after_30_min = range_time.time()


data = pd.read_excel('Data.xlsx', parse_dates=['Arrival Time'],converters={'Train Number or Train Name':str})

def read_Stations(Stations,Destination_parm):
    for item in Stations:
        Station_place_id = item['placeID']
        #print(item["Station_name"])
        filtered_data = data[(data['Place ID'] == Station_place_id) & (data['Arrival Time'].dt.time >= new_time) & (data['Arrival Time'].dt.time <= after_30_min)]
        train= filtered_data['Train Number or Train Name'] 
        arrival =filtered_data.to_dict(orient='records')
        destination =check_destination(train,Destination_parm).to_dict(orient='records')
        return  arrival,destination
   
def check_destination(Train_nos,Destination):    
    target_value = Train_nos.to_string(index=False)
    Check_destination = data[(data['Train Number or Train Name'] == target_value) & (data['Arrival Time'].dt.time >= new_time) ]
    Is_avaibale =  Check_destination[Check_destination['Station Name (Code)'].str.contains(Destination, case=False)]
    return Is_avaibale

def test_api (request):
    Stations_parm = request.GET.get('stations',None)   
    Destination_parm = request.GET.get('destination')
    Time_parm = request.GET.get('time') 

    Stations_parm = json.loads(Stations_parm)

    #print(Stations_parm)

    arrival, destination = read_Stations(Stations_parm,Destination_parm)

    if destination:
      destination= destination           
    else:   
      destination = "No Train Find to Destination " 

    if arrival:
        arrival=arrival
    else:
        arrival ="No any Trains"
    
    response_data = {
        'arrival_data': arrival,
        'destination_data': destination,
    }   

    return JsonResponse(response_data, safe=False)
 