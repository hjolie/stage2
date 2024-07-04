from fastapi import HTTPException


def raise_custom_error(status_code: int, message: str):
    raise HTTPException(
        status_code=status_code,
        detail={"error": True, "message": message}
    )