import mysql.connector
import json, re

db = {"user": "root",
      "password": "abcd1234",
      "host": "127.0.0.1",
      "database": "attractions"}

connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool1",
    pool_size=5,
    **db
)

pool_exec = connection_pool.get_connection()
cursor = pool_exec.cursor()


data_path = "./data/taipei-attractions.json"

with open(data_path, "r") as response:
    data = json.load(response)

spots_list = data["result"]["results"]

for spot in spots_list:
    name = spot["name"]
    category = spot["CAT"]
    description = spot["description"]
    address = spot["address"]
    transport = spot["direction"]
    mrt = spot["MRT"]
    lat = spot["latitude"]
    lng = spot["longitude"]
    images_unfiltered = spot["file"]

    pattern = r"https?://[^\s]+?\.(?:jpg|JPG)"
    images_filtered = re.findall(pattern, images_unfiltered)
    images_json = json.dumps(images_filtered)
    
    add_new_attraction = ("INSERT INTO data "
            "(name, category, description, address, transport, mrt, lat, lng, images) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
    new_attraction_data = (name, category, description, address, transport, mrt, lat, lng, images_json)

    cursor.execute(add_new_attraction, new_attraction_data)
    pool_exec.commit()

if pool_exec.is_connected():
    cursor.close()
    pool_exec.close()