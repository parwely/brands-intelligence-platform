
from fastapi import HTTPException

class BrandNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Brand not found")

class DatabaseConnectionError(HTTPException):
    def __init__(self):
        super().__init__(status_code=503, detail="Database connection failed")