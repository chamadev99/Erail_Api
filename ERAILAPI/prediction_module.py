from database import MySQLConnector
import pandas as pd
import numpy as np
import pickle
import json
import os
from dotenv import load_dotenv
from viewpoints import get_images

load_dotenv()


def make_json_array(keys, values):
    # Create a dictionary from the lists
    data = dict(zip(keys, values))
    # Convert the dictionary to a JSON array

    delay_prediction_json_array = json.dumps([data])
    s3_data = get_images()
    # Print the JSON array
    # print(f"json_array:{json_array}")
    return delay_prediction_json_array, s3_data


# Load the trained ARIMA model from the file
def load_arima_model():
    path = ''
    model_filename = 'arima_model.pkl'
    with open(path+model_filename, 'rb') as model_file:
        loaded_model = pickle.load(model_file)
    return loaded_model


# Define a function to make real-time predictions
def make_real_time_prediction(model, lagged_delay_times):
    try:
        # Convert the lagged delay times to a DataFrame with the same structure as the training data
        lagged_df = pd.DataFrame(np.array(lagged_delay_times).reshape(1, -1), columns=['Lag1', 'Lag2', 'Lag3', 'Lag4', 'Lag5'])

        # Use the ARIMA model to forecast the next station delay based on lagged data
        # print(f"lagged_delay_times:{lagged_delay_times}")
        forecast = model.forecast(steps=1, exog=lagged_df,
                                  # alpha=0.05
                                  )

        forecast_time = forecast[0]

        # print(f"Predicted Delay Time for the Next Station: {forecast_time}")

        return forecast_time

    except Exception as e:
        print("Error in real-time prediction:", e)
        return None


def make_predictions(train_num):
    try:
        db = os.environ.get("DB")
        file_path_train_timetable = 'train_time_tables_v3.xlsx'

        # Load the data into a DataFrame
        df_tt = pd.read_excel(file_path_train_timetable)
        # assign train_id params # eg: 1008
        train_id = train_num

        df_tt_new = df_tt[(df_tt['Train'] == train_id)].copy()
        sort_order = ['Train', 'sort_time']
        df_sorted = df_tt_new.sort_values(by=sort_order)

        db_connection = MySQLConnector()
        db_connection.connect()

        q = f'''SELECT * FROM {db}.delay_prediction WHERE train_id = {train_id}'''
        result = db_connection.execute_query_with_results(query=q)
        db_connection.disconnect()

        delay_df = pd.DataFrame(result, columns=['id', 'train_id', 'station_name', 'delay_reason', 'delay_time',
                                                 'created_at'])

        last_station = str(delay_df['station_name'].tolist()[-1]).lower().strip().replace(" ", "_")
        # print(f"last_station:{last_station}")
        #
        # print(f'delay_df:{delay_df}')
        viewpoint_list = ["pattipola", "idalgashinna", "ohiya", "ella", "haputhale", "demodara", "bandarawela",
                          "badulla"]

        # print(f'viewpoint_list:{viewpoint_list}')
        if len(result) < 5:
            print('Train just started. Need to go few station to do the delay predictions')
            return []

        delay_df['delay_time'].fillna(0, inplace=True)

        # Get the last 5 delay times
        last_5_delays = delay_df['delay_time'].tail(5).tolist()

        # load model
        best_model = load_arima_model()
        if best_model is None:
            print("ARIMA model loading error")
            return []

        # Initialize a list to store the predicted delay times
        predicted_delays = []

        # Loop through the 5 train stations
        for i in range(5):
            # Call the real-time prediction function with the last 5 delay times
            predicted_delay = make_real_time_prediction(best_model, last_5_delays)

            # Append the predicted delay to the list
            predicted_delays.append(predicted_delay)

            # Remove the first value from the list to maintain a window of 5 delay times
            last_5_delays.pop(0)

            # Append the new predicted value at the end
            last_5_delays.append(predicted_delay)

        count = 0
        next_stations = []
        status = 0
        for index, row in df_sorted.iterrows():
            station = str(row['Station']).lower().strip().replace(" ", "_")
            # print(f'station:{station}')
            # print(f'last_station:{last_station}')
            if status != 0:
                count += 1
                next_stations.append(station)
            elif station == last_station:
                count += 1
                next_stations.append(station)
                status = 1
            if count == 5:
                break
        # print(f'predicted_delays:{predicted_delays}')
        # print(f'next_stations:{next_stations}')

        delays, s3_links = make_json_array(keys=next_stations, values=predicted_delays)
        return delays, s3_links

    except Exception as err:
        print(f'err:{err}')
        return []


def predictionIndex():
    res_delay, res_s3 = make_predictions(1006)

    print(res_delay)
    print(res_s3)
