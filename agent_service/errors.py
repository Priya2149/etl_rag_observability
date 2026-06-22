from fastapi import HTTPException


def service_error(message: str, status_code: int = 500):
    raise HTTPException(
        status_code=status_code,
        detail={
            "error": True,
            "message": message
        }
    )