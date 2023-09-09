from ERAILAPI.database import MySQLConnector
import json
from django.http import JsonResponse

def insert_delay(request):
    train_id = request.GET.get('train_no')   
    station_name = request.GET.get('destination')
    delay_reason = request.GET.get('delay_reason') 
    delay_time = request.GET.get('delay_time') 
    print(train_id)
    print(station_name)
    print(delay_reason)
    print(delay_time)

    
    try:
        query = f'''INSERT INTO `etrain`.`delay_prediction` ( `train_id`, `station_name`, `delay_reason`, `delay_time`) 
                    VALUES ({train_id}, '{station_name}', {delay_reason}, {delay_time}); '''

        con = MySQLConnector()
        con.connect()
        con.execute_query(query=query)
        return JsonResponse(True, safe=False)

        

    except Exception as err:
        print(f'form insert error:{err}')
        return JsonResponse(False, safe=False)
       
    
     
   


#insert_delay(1005, "Colombo", 3, 4)
