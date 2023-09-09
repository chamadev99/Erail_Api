from ERAILAPI.database import MySQLConnector


def insert_delay(train_id, station_name, delay_reason, delay_time):
    try:
        query = f'''INSERT INTO `etrain`.`delay_prediction` ( `train_id`, `station_name`, `delay_reason`, `delay_time`) 
                    VALUES ({train_id}, '{station_name}', {delay_reason}, {delay_time}); '''

        con = MySQLConnector()
        con.connect()
        con.execute_query(query=query)
        return True
    except Exception as err:
        print(f'form insert error:{err}')
        return False


# def insert_delay_index(1005, "Colombo", 3, 4)
def insert_delay_index(request):
    train_no_param = request.GET.get('train_no')
    destination_parm = request.GET.get('destination')
    timedelay_reasone_parm = request.GET.get('timedelay_reasone')
    delay_time_parm = request.GET.get('delay_time')
    print(train_no_param)
    print(destination_parm)
    print(timedelay_reasone_parm)
    print(delay_time_parm)

    insert_delay_index(train_no_param, destination_parm, timedelay_reasone_parm, delay_time_parm)
