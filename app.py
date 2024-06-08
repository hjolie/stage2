import json
from typing import List
from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import mysql.connector
from pydantic import BaseModel

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

db = {"user": "root",
	"password": "abcd1234",
	"host": "127.0.0.1",
	"database": "attractions"}

connection_pool = mysql.connector.pooling.MySQLConnectionPool(
pool_name="pool0",
pool_size=5,
**db
)

def get_connection():
	try:
		connection = connection_pool.get_connection()
		yield connection
	finally:
		if connection:
			connection.close()


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


@app.get("/api/attractions", response_model=AttractionsResponse, responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_attractions(page: int = Query(0, ge=0), keyword: str = Query(None), connection=Depends(get_connection)):
	if keyword:
		try:
			query_keyword = ("SELECT * FROM data "
					"WHERE name LIKE %s OR mrt = %s "
					"ORDER BY id "
					"LIMIT 12 OFFSET %s;")
			offset = page * 12
			params = ("%" + keyword + "%", keyword, offset)
			cursor = connection.cursor()
			cursor.execute(query_keyword, params)
			result = cursor.fetchall()
		except Exception:
			raise_custom_error(500, "Internal Server Error")
		finally:
			if cursor:
				cursor.close()
		
		if result:
			keys = ["id", "name", "category", "description", "address", "transport", "mrt", "lat", "lng", "images"]

			attractions_list_by_keyword = [dict(zip(keys, attraction)) for attraction in result]

			for attraction in attractions_list_by_keyword:
				attraction["images"] = json.loads(attraction["images"])
			
			if attractions_list_by_keyword == []:
				raise_custom_error(404, "Data Not Found")
			elif len(attractions_list_by_keyword) < 12:
				next_page = None
			else:
				next_page = page + 1
		else:
			raise_custom_error(404, "Data Not Found")
		
		return AttractionsResponse(
			nextPage = next_page,
			data = attractions_list_by_keyword
		)
	else:
		try:
			query_paginated = ("SELECT * FROM data "
						"ORDER BY id "
						"LIMIT 12 OFFSET %s;")
			offset = page * 12
			cursor = connection.cursor()
			cursor.execute(query_paginated, (offset,))
			result = cursor.fetchall()
		except Exception:
			raise_custom_error(500, "Internal Server Error")
		finally:
			if cursor:
				cursor.close()
		
		keys = ["id", "name", "category", "description", "address", "transport", "mrt", "lat", "lng", "images"]

		attractions_list = [dict(zip(keys, attraction)) for attraction in result]

		for attraction in attractions_list:
			attraction["images"] = json.loads(attraction["images"])

		if attractions_list == []:
			raise_custom_error(404, "Data Not Found")
		elif len(attractions_list) < 12:
			next_page = None
		else:
			next_page = page + 1

		return AttractionsResponse(
			nextPage = next_page,
			data = attractions_list
		)

@app.get("/api/attraction/{attractionId}", response_model=AttractionResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_attraction_by_id(attractionId: int, connection=Depends(get_connection)):
	try:
		query_by_id = ("SELECT * FROM data "
					"WHERE id = %s;")
		cursor = connection.cursor()
		cursor.execute(query_by_id, (attractionId,))
		result = cursor.fetchone()
	except Exception:
		raise_custom_error(500, "Internal Server Error")
	finally:
		if cursor:
			cursor.close()
	
	if result:
		keys = ["id", "name", "category", "description", "address", "transport", "mrt", "lat", "lng", "images"]

		attraction_by_id = dict(zip(keys, result))
		attraction_by_id["images"] = json.loads(attraction_by_id["images"])

		return AttractionResponse(
		data = attraction_by_id
		)
	else:
		raise_custom_error(400, "Incorrect or Invalid Attraction Id")

@app.get("/api/mrts", response_model=MrtResponse, responses={500: {"model": ErrorResponse}})
async def get_mrts(connection=Depends(get_connection)):
	try:
		query_mrt_count = ("SELECT mrt, COUNT(id) AS mrt_count "
							"FROM data "
							"GROUP BY mrt "
							"ORDER BY mrt_count DESC;")
		cursor = connection.cursor()
		cursor.execute(query_mrt_count)
		result = cursor.fetchall()
	except Exception:
		raise_custom_error(500, "Internal Server Error")
	finally:
		if cursor:
			cursor.close()
	
	mrts_list = []
	for mrt_count in result:
		mrts_list.append(mrt_count[0])
	
	mrts_list_filtered = [mrt for mrt in mrts_list if mrt is not None]

	return MrtResponse(data = mrts_list_filtered)

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