from fastapi import HTTPException
from pydantic import BaseModel

class ErrorResponse(BaseModel):
	error: bool
	message: str

def raise_custom_error(status_code: int, message: str):
    raise HTTPException(
        status_code=status_code,
        detail={"error": True, "message": message}
    )