from http.client import HTTPException
import httpx
from dotenv import load_dotenv
import os

load_dotenv()
partner_key = os.getenv("partner_key")
merchant_id = os.getenv("merchant_id")
url = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
headers = {
    "Content-Type": "application/json",
    "x-api-key": partner_key
}

async def pay_by_prime(prime, price, contact_phone, contact_name, contact_email, attraction_address):
	data = {
		"prime": prime,
		"partner_key": partner_key,
		"merchant_id": merchant_id,
		"amount": price,
		"details": "TapPay Test",
		"cardholder": {
			"phone_number": contact_phone,
			"name": contact_name,
			"email": contact_email,
			"zip_code": "100",
			"address": attraction_address,
			"national_id": "A123456789"
		}
	}

	async with httpx.AsyncClient() as client:
		response = await client.post(url, headers=headers, json=data)
		if response.status_code == 200:
			return response.json()
		else:
			raise HTTPException(status_code=response.status_code, detail=response.text)