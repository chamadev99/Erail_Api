import pandas as pd
from datetime import datetime,timedelta
import numpy as np
import json
from django.http import JsonResponse
from .serializers import TraiSerializers
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

data = pd.read_excel('S11.xlsx', parse_dates=['Arrival Time'],converters={'Train Number or Train Name':str})

def read_Stations(Stations,Destination_parm,current_time,after_30_min):
    
    for item in Stations:
        Station_place_id = item['placeID']
        
        filtered_data = data[(data['Place ID'] == Station_place_id) & (data['Arrival Time'].dt.time >= current_time.time()) & (data['Arrival Time'].dt.time <= after_30_min.time())]        
        Near_by_Station = data[(data['Place ID'] == Station_place_id)]
        Near_by_Stations=Near_by_Station['Station Name (Code)'].unique()
        Near_Stations=Near_by_Stations[0]     
                 
        train= filtered_data['Train Number or Train Name']        
        arrival,destination, a,a_last,transitr_start,transit =check_destination(Near_Stations,train,Destination_parm,current_time,Station_place_id)  
    
        return  arrival.to_dict(orient='records'),destination.to_dict(orient='records'),a,a_last,transitr_start,transit
   
def check_destination(Near_Stations,Train_nos,Destination,current_time,Station_place_id):  
    target_value = Train_nos.to_string(index=False)  
    trains = target_value.split('\n')
    train_array = [line.strip() for line in trains]  
    Near_Station=[]           
    Near_Station_last=[]
    transit_start=[]
    transit_data=[]      
 
    for data_fragment in train_array:   
       
        Is_arrival , Is_destination= process_data(data_fragment,Destination,current_time,Station_place_id)         

        if Is_destination.empty:
            Is_arrival, Is_destination= process_data(data_fragment,Destination,current_time,Station_place_id)   
        else:
                break 

    if Is_destination.empty:                                     
                   Near_Station,Near_Station_last,transit_start,transit_data= Transit(Near_Stations,Destination,train_array)                
     
    return Is_arrival,Is_destination,Near_Station,Near_Station_last,transit_start,transit_data
 
def process_data(data_fragment,Destination,current_time,Station_place_id): 

    Check_destination = data[(data['Train Number or Train Name'] == data_fragment)]       
    Check_destination['Arrival Time'] = Check_destination['Arrival Time'].apply(lambda timestamp: timestamp.strftime('%H:%M %p'))
    Check_destination['Departure Time'] = Check_destination['Departure Time'].apply(lambda timestamp: timestamp.strftime('%H:%M %p'))
    to_destination = Check_destination[Check_destination['Station Name (Code)'].str.contains(Destination)] #check user entered destination is match    

    to_arrival = Check_destination[(Check_destination['Place ID'] == Station_place_id)]      
    return to_arrival,to_destination

def Transit(Near_Stations,Destination,train_array):
    Is_Up_Or_Down=CheckUpDown(Near_Stations,Destination)#check user destination is up or down
    my_trains=GetUpDownTrains(train_array,Is_Up_Or_Down)#get related up or down trains   

    if not my_trains:
         Near_Station=[]
         Near_Station_last=[]
         is_have=[]
         is_start=[]
         return Near_Station,Near_Station_last,is_have         
    else:                         
    
        for train_code in my_trains:
                #read train data one by one  
                last_station = data[(data['Train Number or Train Name'] == train_code)] 
                last_station['Departure Time'] = last_station['Departure Time'].apply(lambda timestamp: timestamp.strftime('%H:%M %p'))
                Near_Station= last_station[last_station['Station Name (Code)'].str.contains(Near_Stations)] 

                Near_Station_last = last_station.iloc[-1]
                last_station=Near_Station_last['Station Name (Code)']#train last stop station
                last_arrival_time=Near_Station_last['Arrival Time']#train last stop arrival time                    
                                
                is_start,is_have=CatchDestination(last_station,last_arrival_time,Destination,Is_Up_Or_Down) #check that train destination   
                
        return Near_Station,Near_Station_last,is_start,is_have

def CheckUpDown(Near_Stations,Destination):
    Station_data = pd.read_excel('Station.xlsx')
    Get_arrival_point=Station_data[(Station_data['Station Name'] == Near_Stations)]
    Get_destination_point=Station_data[(Station_data['Station Name'] == Destination)]

    arrival_point_index=Get_arrival_point['Index'].iloc[0]
    destination_point_index=Get_destination_point['Index'].iloc[0]  
    
    #after_60_min =train_time +timedelta(minutes=60)
    if arrival_point_index > destination_point_index:
         return "Downwards"
    else:
         return "Upwards"  
   
def GetUpDownTrains(trains,Is_Up_Or_Down): #trains means nearest station with in time available trains
        #print(trains)  
        unique_train_names_array = []
        for train in trains: 
            #check that timeperiod avaiabale trains are up or down (related )
            Check_destination = data[(data['Train Number or Train Name'] == train) & (data['Train Up or Down'] ==Is_Up_Or_Down ) ]   

            if not Check_destination.empty:
                        my_trains=Check_destination['Train Number or Train Name'].unique()
                        
                        for train_name in my_trains:                            
                                    unique_train_names_array.append(train_name)

                        #print(my_trains)                                 
          
        return unique_train_names_array

def CatchDestination(last_station,last_arrival_time,Destination,Is_Up_Or_Down):    
    arrival_time_30_min=last_arrival_time + timedelta(hours=2)      

    filtered_data = data[(data['Station Name (Code)'] == last_station) & (data['Arrival Time'].dt.time >= last_arrival_time.time()) & (data['Arrival Time'].dt.time <= arrival_time_30_min.time()) & (data['Train Up or Down'] == Is_Up_Or_Down)]        
    filtered_data['Arrival Time'] = filtered_data['Arrival Time'].apply(lambda timestamp: timestamp.strftime('%H:%M %p'))
    
    train= filtered_data['Train Number or Train Name'] 
    target_value = train.to_string(index=False)  
    trains = target_value.split('\n')
    train_array = [line.strip() for line in trains]
    filtered_train_data = None
    filtered_train_data_start =None        
     
    for to_chcek in train_array:
        
        filtered_train_data_start = data[(data['Train Number or Train Name'] == to_chcek) & (data['Station Name (Code)'] == last_station)]
        filtered_train_data = data[(data['Train Number or Train Name'] == to_chcek) & (data['Station Name (Code)'] == Destination)]

        #convert date tome in to the time formate H:M:AM or PM
        filtered_train_data_start['Arrival Time'] = filtered_train_data_start['Arrival Time'].apply(lambda timestamp: timestamp.strftime('%H:%M %p'))
        filtered_train_data_start['Departure Time'] = filtered_train_data_start['Departure Time'].apply(lambda timestamp: timestamp.strftime('%H:%M %p'))
        filtered_train_data['Arrival Time'] = filtered_train_data['Arrival Time'].apply(lambda timestamp: timestamp.strftime('%H:%M %p'))
        filtered_train_data['Departure Time'] = filtered_train_data['Departure Time'].apply(lambda timestamp: timestamp.strftime('%H:%M %p'))

        if  filtered_data.empty:
             print("stop")

        else:
             filtered_train_data = data[(data['Train Number or Train Name'] == to_chcek)]

             #convert date tome in to the time formate H:M:AM or PM
             filtered_train_data['Arrival Time'] = filtered_train_data['Arrival Time'].apply(lambda timestamp: timestamp.strftime('%H:%M %p'))

             filtered_train_data=filtered_train_data.tail(1)            
                                      
             break

    return filtered_train_data_start,filtered_train_data
   
def Ml_Model(time):
    UD_Data = pd.read_csv('erail.csv')

    UD_Data['Arrival Time'] = pd.to_datetime(UD_Data['Arrival Time'], format='%I:%M:%S %p')

    UD_Data['Hour'] = UD_Data['Arrival Time'].dt.hour
    UD_Data['Minute'] = UD_Data['Arrival Time'].dt.minute

    # Splitting into X and y
    X = UD_Data[['Hour', 'Minute']].values
    y = UD_Data['Train Up or Down'].values

    X_df = pd.DataFrame(X, columns=['Hour', 'Minute'])
    y_df = pd.DataFrame(y, columns=['Train Up or Down'])

    X_train, X_test, y_train, y_test = train_test_split(X_df, y_df, test_size=0.2)

    model = DecisionTreeClassifier()
    model.fit(X_train, y_train)
    model.predict(X_test)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    #print("Accuracy:", accuracy)

   # input_time_str = time.time() # Example input time
    input_time = pd.to_datetime(time)
    input_hour = input_time.hour
    input_minute = input_time.minute

    input_data = pd.DataFrame([[input_hour, input_minute]], columns=['Hour', 'Minute'])
    predicted_direction = model.predict(input_data)

    if predicted_direction == 1:
        return "Down"
    else:
        return "Up"    

def test_api (request):
    Stations_parm = request.GET.get('stations',None)   
    Destination_parm = request.GET.get('destination')
    Time_parm = request.GET.get('time') 

    current_time = datetime.strptime(Time_parm, '%H:%M:%S')
    after_30_min = current_time + timedelta(minutes=30) 
   
    
    Stations_parm = json.loads(Stations_parm)    

    arrival, destination ,a ,a_last,transitr_start,trasit = read_Stations(Stations_parm,Destination_parm,current_time,after_30_min)
    UD = Ml_Model(after_30_min)   

  
    if destination:
      destination= destination           
    else:   
      destination ='null' 

    if arrival:
        arrival=arrival
    else:
        arrival ='null'

    if isinstance (a,list):
         transit_arrival ='null'
    elif isinstance(a,pd.DataFrame):
         transit_arrival=a.to_dict(orient='records')

    if isinstance (a_last,list):
         transit_destination_1 ='null'
    elif isinstance(a_last,pd.Series):        
         transit_destination_1=a_last.to_dict()

    if isinstance (transitr_start,list):
         trasit_final_start ='null'
    elif isinstance(transitr_start,pd.DataFrame):
         trasit_final_start=transitr_start.to_dict(orient='records')        


    if isinstance (trasit,list):
         trasit_final_destination ='null'
    elif isinstance(trasit,pd.DataFrame):
         trasit_final_destination=trasit.to_dict(orient='records')
    
    response_data = {
        'arrival_data': arrival,
        'destination_data': destination,
        'ml_data':UD,
        'transit_arrival':transit_arrival,
        'transit_destination_1':transit_destination_1,
        'trasit_final_start':trasit_final_start,
        'trasit_final_destination':trasit_final_destination,      
    }   

    return JsonResponse(response_data, safe=False)
 