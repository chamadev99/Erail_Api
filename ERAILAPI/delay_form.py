from database import MySQLConnector


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


insert_delay(1005, "Colombo", 3, 4)
