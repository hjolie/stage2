import mysql.connector

db = {"user": "root",
	"password": "abcd1234",
	"host": "127.0.0.1",
	"database": "attractions"}

connection_pool = mysql.connector.pooling.MySQLConnectionPool(
pool_name="pool0",
pool_size=5,
**db
)