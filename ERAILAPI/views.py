import pandas as pd
from datetime import datetime,timedelta

import json
from django.http import JsonResponse
from .serializers import TraiSerializers



minutes = 4 #min
between_minutes = 30 #min

#current_time = datetime.now().replace(hour=10, minute=50)
#new_time = current_time.strftime("%H:%M")
#current_time = datetime.strptime('10:50:00', '%H:%M:%S')
# Increment the time by 30 minutes
#after_30_min = current_time + timedelta(minutes=30)
#after_30_min = after_min.strftime("%H:%M")

#print(current_time)
#print(after_30_min)

# increment = timedelta(minutes=minutes)
# range = timedelta(minutes=between_minutes)

# range_time = current_time + range
# after_30_min = range_time.time()


data = pd.read_excel('new_rp.xlsx', parse_dates=['Arrival Time'],converters={'Train Number or Train Name':str})

def read_Stations(Stations,Destination_parm,current_time,after_30_min):

    
    for item in Stations:
        Station_place_id = item['placeID']
        #print(item["Station_name"])
        filtered_data = data[(data['Place ID'] == Station_place_id) & (data['Arrival Time'].dt.time >= current_time.time()) & (data['Arrival Time'].dt.time <= after_30_min.time())]
        filtered_data['Arrival Time'] = filtered_data['Arrival Time'].apply(lambda timestamp: timestamp.strftime('%H:%M'))
        train= filtered_data['Train Number or Train Name'] 
        arrival =filtered_data.to_dict(orient='records')
        destination =check_destination(train,Destination_parm,current_time).to_dict(orient='records')
        return  arrival,destination
   
def check_destination(Train_nos,Destination,current_time):  
    target_value = Train_nos.to_string(index=False)
    
   
    Check_destination = data[(data['Train Number or Train Name'] == target_value) & (data['Arrival Time'].dt.time >= current_time.time()) ]
    
    Is_avaibale =  Check_destination[Check_destination['Station Name (Code)'].str.contains(Destination)]
   
   
    return Is_avaibale

def test_api (request):
    Stations_parm = request.GET.get('stations',None)   
    Destination_parm = request.GET.get('destination')
    Time_parm = request.GET.get('time') 

    current_time = datetime.strptime(Time_parm, '%H:%M:%S')
    after_30_min = current_time + timedelta(minutes=30) 
    
    Stations_parm = json.loads(Stations_parm)    

    arrival, destination = read_Stations(Stations_parm,Destination_parm,current_time,after_30_min)
    print(destination)
  
    if destination:
      destination= destination           
    else:   
      destination ='null' 

    if arrival:
        arrival=arrival
    else:
        arrival ='null'
    
    response_data = {
        'arrival_data': arrival,
        'destination_data': destination
    }   

    return JsonResponse(response_data, safe=False)
 