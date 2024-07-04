from pydantic import BaseModel
from typing import List

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

class UserContact(BaseModel):
	name: str
	email: str
	phone: str

class OrderAttraction(BaseModel):
	attraction: BookingAttraction
	date: str
	time: str

class Order(BaseModel):
	price: int
	trip: OrderAttraction
	contact: UserContact

class CreateOrder(BaseModel):
	prime: str
	order: Order

class Payment(BaseModel):
	status: int
	message: str

class PaymentResponse(BaseModel):
	number: str
	payment: Payment