from datetime import timedelta
import json
from typing import List
from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import mysql.connector
from pydantic import BaseModel
from auth import EXPIRE_DAYS, gen_token, verify_token, get_user_id_from_token

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

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserSignIn(BaseModel):
    email: str
    password: str

class BookingInput(BaseModel):
	attractionId: int
	date: str
	time: str
	price: int

class BookingAttraction(BaseModel):
    id: int
    name: str
    address: str
    image: str

class Booking(BaseModel):
	attraction: BookingAttraction
	date: str
	time: str
	price: int

class Token(BaseModel):
    token: str | None = None

class TokenData(BaseModel):
    data: dict | None = None

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


@app.post("/api/booking", responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def book(booking_input: BookingInput, authorization: str = Header(...), connection=Depends(get_connection)):
	try:
		token = authorization.split(" ")[1]
		user_id = get_user_id_from_token(token)
	except Exception:
		raise_custom_error(403, "Signin Error - Invalid Token")

	try:
		find_booking = ("SELECT id FROM booking "
				"WHERE user_id = %s")
		cursor = connection.cursor()
		cursor.execute(find_booking, (user_id,))
		result = cursor.fetchall()
	except Exception:
		raise_custom_error(500, "Internal Server Error - Finding Booking")
	finally:
		if cursor:
			cursor.close()

	if result:
		try:
			delete_attraction = ("DELETE FROM booking "
						"WHERE id = %s")
			cursor = connection.cursor()
			id = result[0][0]
			cursor.execute(delete_attraction, (id,))
			connection.commit()
		except Exception:
			raise_custom_error(500, "Internal Server Error - Deleting Existing Booking")
		finally:
			if cursor:
				cursor.close()
	
	try:
		attractionId = booking_input.attractionId
		date = booking_input.date
		time = booking_input.time
		price = booking_input.price
	except Exception:
		raise_custom_error(400, "Invalid Input Data")

	try:
		save_attraction = ("INSERT INTO booking "
						"(user_id, attraction_id, date, time, price) "
						"VALUES (%s, %s, %s, %s, %s)")
		booking_data = (user_id, attractionId, date, time, price)
		cursor = connection.cursor()
		cursor.execute(save_attraction, booking_data)
		connection.commit()
		return {"ok": True}
	except Exception:
			raise_custom_error(500, "Internal Server Error - Saving Booking")
	finally:
		if cursor:
			cursor.close()

@app.get("/api/booking", responses={403: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_booking(authorization: str = Header(...), connection=Depends(get_connection)):
	try:
		token = authorization.split(" ")[1]
		user_id = get_user_id_from_token(token)
	except Exception:
		raise_custom_error(403, "Signin Error - Invalid Token")

	try:
		find_booking = ("SELECT attraction_id, date, time, price FROM booking "
				"WHERE user_id = %s")
		cursor = connection.cursor()
		cursor.execute(find_booking, (user_id,))
		booking_result = cursor.fetchall()
	except Exception:
		raise_custom_error(500, "Internal Server Error - Finding Booking")
	finally:
		if cursor:
			cursor.close()
	
	if booking_result:
		for (attraction_id, date, time, price) in booking_result:
			attraction_id = attraction_id
			date = date
			time = time
			price = price
		
		try:
			find_attraction = ("SELECT name, address, images FROM data "
					"WHERE id = %s")
			cursor = connection.cursor()
			cursor.execute(find_attraction, (attraction_id,))
			attraction_result = cursor.fetchall()
			
			for (name, address, images) in attraction_result:
				name = name
				address = address
				images = images
			
			images = json.loads(images)
			image = images[0]
			attraction = BookingAttraction(
				id = attraction_id,
				name = name,
				address = address,
				image = image
			)
			booking = Booking(
				attraction=attraction,
				date=date,
				time=time,
				price=price
			)
			return {"data": booking}
		except Exception:
			raise_custom_error(500, "Internal Server Error - Finding Attraction")
		finally:
			if cursor:
				cursor.close()
	else:
		return {"data": None}	

@app.delete("/api/booking", responses={403: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_booking(authorization: str = Header(...), connection=Depends(get_connection)):
	try:
		token = authorization.split(" ")[1]
		user_id = get_user_id_from_token(token)
	except Exception:
		raise_custom_error(403, "Signin Error - Invalid Token")
	
	try:
		delete_booking = ("DELETE FROM booking "
				"WHERE user_id = %s")
		cursor = connection.cursor()
		cursor.execute(delete_booking, (user_id,))
		connection.commit()
		return {"ok": True}
	except Exception:
		raise_custom_error(500, "Internal Server Error - Deleting Booking")
	finally:
		if cursor:
			cursor.close()

@app.post("/api/user", responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def register_user(user: UserRegister, connection=Depends(get_connection)):
	name = user.name
	email = user.email
	password = user.password

	try:
		find_user = ("SELECT * FROM user "
			"WHERE email = %s")
		cursor = connection.cursor()
		cursor.execute(find_user, (email,))
		result = cursor.fetchall()
	except Exception:
		raise_custom_error(500, "Internal Server Error - Finding User")
	finally:
		if cursor:
			cursor.close()

	if result:
		raise_custom_error(400, "This email has been registered.")
	else:
		try:
			add_new_user = ("INSERT INTO user "
					"(name, email, password) "
					"VALUES(%s, %s, %s)")
			new_user_data = (name, email, password)
			cursor = connection.cursor()
			cursor.execute(add_new_user, new_user_data)
			connection.commit()
			return {"ok": True}
		except Exception:
			raise_custom_error(500, "Internal Server Error - Adding New User")
		finally:
			if cursor:
				cursor.close()

@app.put("/api/user/auth", responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def signin(user: UserSignIn, connection=Depends(get_connection)):
	email = user.email
	password = user.password
	
	try:
		find_user = ("SELECT id, name FROM user "
			"WHERE email = %s "
			"and password = %s")
		user_credential = (email, password)
		cursor = connection.cursor()
		cursor.execute(find_user, user_credential)
		result = cursor.fetchall()
	except Exception:
		raise_custom_error(500, "Internal Server Error - Verifying User")
	finally:
		if cursor:
			cursor.close()
	
	if result:
		for (id, name) in result:
			user_id = id
			user_name = name
		user_data = {
			"user_id": user_id,
			"name": user_name,
			"email": email
		}
		token_expires = timedelta(days=EXPIRE_DAYS)
		token = gen_token(
        data=user_data, expires_delta=token_expires
    )
		return Token(token=token)
	else:
		raise_custom_error(400, "Incorrect Email or Password.")

@app.get("/api/user/auth")
async def get_user_data(authorization: str = Header(...)):
	try:
		token = authorization.split(" ")[1]
		data = verify_token(token)
		if data:
			return TokenData(data=data)
	except Exception:
		return TokenData(data=None)

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