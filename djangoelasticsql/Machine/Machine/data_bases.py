import mysql.connector
from elasticsearch import Elasticsearch

# Function to connect to MySQL
def connect_to_mysql():
    
    return mysql.connector.connect(
        host="localhost",
        user="------",
        password="----------",
        database="data"
    )



# Function to connect to Elasticsearch
def connect_to_elasticsearch():
    es = Elasticsearch("http://localhost:9200")
    if es.ping():
        return es
    return None

# Calling the functions
mysql_connection = connect_to_mysql()
elasticsearch_connection = connect_to_elasticsearch()

# Output confirmation
print("Connected to MySQL" if mysql_connection else "MySQL connection failed")
print("Successfully connected to Elasticsearch" if elasticsearch_connection else "Elasticsearch connection failed")
