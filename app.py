from datetime import timedelta
import json
import uuid
from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from models.AttractionModels import get_attraction_by_id, get_attractions, get_attractions_by_keyword
from models.BookingModels import create_booking, delete_booking, find_booking, get_attraction, get_booking
from ErrorHandler import raise_custom_error, ErrorResponse
from models.MrtModel import get_mrts
from models.OrderModels import create_order_data, delete_booking_page_data, get_order_id, save_payment_failed, save_payment_success, update_order_status
from TapPay import pay_by_prime
from models.UserModels import find_user, signin_user, signup_user
from auth import EXPIRE_DAYS, gen_token, verify_token, get_user_id_from_token
from PydanticModels import AttractionResponse, AttractionsResponse, Booking, BookingAttraction, BookingInput, CreateOrder, MrtResponse, Payment, PaymentResponse, Token, TokenData, UserRegister, UserSignIn

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


@app.post("/api/orders", responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def handle_create_order(create_order: CreateOrder, authorization: str = Header(...)):
	try:
		token = authorization.split(" ")[1]
		user_id = get_user_id_from_token(token)
	except Exception:
		raise_custom_error(403, "Signin Error - Invalid Token")

	try:
		prime = create_order.prime
		order = create_order.order
		attraction = order.trip.attraction
		contact = order.contact
		price = order.price

		attraction_id = attraction.id
		attraction_name = attraction.name
		attraction_address = attraction.address
		
		date = order.trip.date
		time = order.trip.time

		contact_name = contact.name
		contact_email = contact.email
		contact_phone = contact.phone

		uuid_number = uuid.uuid4()
		order_number = str(uuid_number)

		create_order_data(order_number, user_id, attraction_id, attraction_name, date, time, price, contact_name, contact_email, contact_phone) #status set default unpaid 

		result_order_id = get_order_id(order_number)
		order_id = result_order_id[0]
		
		result_payment = await pay_by_prime(prime, price, contact_phone, contact_name, contact_email, attraction_address)

		status = result_payment.get("status")
		msg = result_payment.get("msg")
		rec_trade_id = result_payment.get("rec_trade_id")
		merchant_id = result_payment.get("merchant_id")

		if status == 0:
			amount = result_payment.get("amount")
			acquirer = result_payment.get("acquirer")
			currency = result_payment.get("currency")
			bank_transaction_id = result_payment.get("bank_transaction_id")
			auth_code = result_payment.get("auth_code")
			card_info = result_payment.get("card_info")
			last_four = card_info.get("last_four")
			bin_code = card_info.get("bin_code")

			save_payment_success(order_id, status, msg, amount, acquirer, currency, rec_trade_id, bank_transaction_id, auth_code, last_four, bin_code, merchant_id)

			update_order_status(order_id)
			delete_booking_page_data(user_id)
		else:
			save_payment_failed(order_id, status, msg, rec_trade_id, merchant_id)
		
		payment = Payment(
			status = status,
			message = msg
			)
		payment_response = PaymentResponse(
			number = order_number,
			payment = payment
			)
		return {"data": payment_response}
	except Exception:
		raise_custom_error(400, "Order Error - Failed to Create New Order and Complete Payment Process")
	
@app.post("/api/booking", responses={400: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def handle_create_booking(booking_input: BookingInput, authorization: str = Header(...)):
	try:
		token = authorization.split(" ")[1]
		user_id = get_user_id_from_token(token)
	except Exception:
		raise_custom_error(403, "Signin Error - Invalid Token")

	result = find_booking(user_id)

	if result:
		id = result[0][0]
		delete_booking(id)
	
	try:
		attractionId = booking_input.attractionId
		date = booking_input.date
		time = booking_input.time
		price = booking_input.price
	except Exception:
		raise_custom_error(400, "Invalid Input Data")

	result_booking = create_booking(user_id, attractionId, date, time, price)
	return result_booking

@app.get("/api/booking", responses={403: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def handle_get_booking(authorization: str = Header(...)):
	try:
		token = authorization.split(" ")[1]
		user_id = get_user_id_from_token(token)
	except Exception:
		raise_custom_error(403, "Signin Error - Invalid Token")

	result = get_booking(user_id)
	
	if result:
		for (attraction_id, date, time, price) in result:
			attraction_id = attraction_id
			date = date
			time = time
			price = price
		
		attraction_result = get_attraction(attraction_id)

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
	else:
		return {"data": None}	

@app.delete("/api/booking", responses={403: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def handle_delete_booking(authorization: str = Header(...)):
	try:
		token = authorization.split(" ")[1]
		user_id = get_user_id_from_token(token)
	except Exception:
		raise_custom_error(403, "Signin Error - Invalid Token")
	
	result = delete_booking(user_id)
	return result

@app.post("/api/user", responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def handle_register_user(user: UserRegister):
	name = user.name
	email = user.email
	password = user.password

	result = find_user(email)

	if result:
		raise_custom_error(400, "This email has been registered.")
	else:
		result_signup = signup_user(name, email, password)
		return result_signup

@app.put("/api/user/auth", responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def signin(user: UserSignIn):
	email = user.email
	password = user.password
	
	result = signin_user(email, password)
	
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
async def handle_attractions(page: int = Query(0, ge=0), keyword: str = Query(None)):
	if keyword:
		result = get_attractions_by_keyword(page, keyword)
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
		result = get_attractions(page)

		if result:
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
		else:
			raise_custom_error(404, "Data Not Found")

		return AttractionsResponse(
			nextPage = next_page,
			data = attractions_list
		)

@app.get("/api/attraction/{attractionId}", response_model=AttractionResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def handle_attraction_by_id(attractionId: int):
	result = get_attraction_by_id(attractionId)
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
async def handle_mrts():
	result = get_mrts()
	
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