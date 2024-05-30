from collections import Counter
import json
from typing import List
from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
import mysql.connector
from pydantic import BaseModel

app = FastAPI()

def get_db_data():
	db = {"user": "root",
      "password": "abcd1234",
      "host": "127.0.0.1",
      "database": "attractions"}

	connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool0",
    pool_size=5,
    **db
)

	pool_exec = connection_pool.get_connection()
	cursor = pool_exec.cursor()
	
	cursor.execute("SELECT * FROM data")
	result = cursor.fetchall()

	if pool_exec.is_connected():
		cursor.close()
		pool_exec.close()
	
	keys = ["id", "name", "category", "description", "address", "transport", "mrt", "lat", "lng", "images"]

	attractions_data = [dict(zip(keys, attraction)) for attraction in result]

	for attraction in attractions_data:
		attraction["images"] = json.loads(attraction["images"])
	
	return attractions_data

attractions_list = get_db_data()

class AttractionsResponse(BaseModel):
	nextPage: int | None = None
	data: List[dict]

class AttractionResponse(BaseModel):
	data: dict

class MrtResponse(BaseModel):
	data: list[str]

class ErrorResponse(BaseModel):
	error: bool
	message: str

def raise_custom_error(status_code: int, message: str):
    raise HTTPException(
        status_code=status_code,
        detail={"error": True, "message": message}
    )

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

def paginate(q_page, q_limit, data_list):
	start = q_page * q_limit
	end = start + q_limit
	total_items = len(data_list)

	if start >= total_items:
		raise_custom_error(404, "Data Not Found")
	elif total_items < end:
		next_page = None
		paginated_items = data_list[start:total_items]
	else:
		next_page = q_page + 1
		paginated_items = data_list[start:end]
	
	return next_page, paginated_items

@app.get("/api/attractions", response_model=AttractionsResponse, responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_attractions(page: int = Query(0, ge=0), limit: int = Query(12), keyword: str = Query(None)):
	if attractions_list is None:
		raise_custom_error(500, "Internal Server Error")

	if keyword:
		filtered_data = [item for item in attractions_list if keyword in item["name"] or keyword == item["mrt"]]

		if filtered_data:
			next_page, paginated_items = paginate(page, limit, filtered_data)
		else:
			raise_custom_error(404, "Data Not Found")
		
		return AttractionsResponse(
			nextPage = next_page,
			data = paginated_items
		)
	
	next_page, paginated_items = paginate(page, limit, attractions_list)

	return AttractionsResponse(
		nextPage = next_page,
		data = paginated_items
    )

@app.get("/api/attraction/{attractionId}", response_model=AttractionResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_attraction_by_id(attractionId: int):
	if attractions_list is None or attractionId is None:
		raise_custom_error(500, "Internal Server Error")

	filtered_data = [item for item in attractions_list if attractionId == item["id"]]

	if filtered_data:
		return AttractionResponse(
		data = filtered_data[0]
	)
	else:
		raise_custom_error(400, "Incorrect or Invalid Id")

@app.get("/api/mrts", response_model=MrtResponse, responses={500: {"model": ErrorResponse}})
async def get_mrts(mrts_list: list=[], sorted_mrts_list: list=[]):
	try:
		for i in range(len(attractions_list)):
			mrts_list.append(attractions_list[i]["mrt"])
		
		stations = [station for station in mrts_list if station is not None]

		station_counts = Counter(stations)

		sorted_stations = sorted(station_counts.items(), key=lambda x: x[1], reverse=True)

		for station, count in sorted_stations:
			sorted_mrts_list.append(station)

		return MrtResponse(data = sorted_mrts_list)
	except Exception:
		raise_custom_error(500, "Internal Server Error")

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")