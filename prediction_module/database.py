import mysql.connector
from dotenv import load_dotenv
import os


load_dotenv()


class MySQLConnector:
    def __init__(self):
        self.host = os.environ.get("DB_HOST")
        self.username = os.environ.get("DB_UN")
        self.password = os.environ.get("DN_PWD")
        self.database = os.environ.get("DB")
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                database=self.database
            )
            print("Connected to MySQL database")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected from MySQL database")

    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            print("Query executed successfully")
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")

    def execute_query_with_results(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except mysql.connector.Error as err:
            print(f"Error executing query with results: {err}")
            return None


# Example usage:
if __name__ == "__main__":

    connector = MySQLConnector()
    connector.connect()

    # # Example query with parameters
    # query = "INSERT INTO my_table (column1, column2) VALUES (%s, %s)"
    # params = ("value1", "value2")
    # connector.execute_query(query, params)
    #
    # # Example query with parameters and results
    # query = "SELECT * FROM my_table WHERE column1 = %s"
    # params = ("value1",)
    # results = connector.execute_query_with_results(query, params)
    # if results:
    #     for row in results:
    #         print(row)

    connector.disconnect()
