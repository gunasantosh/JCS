from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api.routes import users, core
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s',
)

app = FastAPI(title="My FastAPI App")

# Include routers
app.include_router(users.router)
app.include_router(core.router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Log the detailed error internally (server-side only)
    print(f"Validation error: {exc.errors()}")
    
    # Return a user-friendly error response
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request format. Please ensure all required fields are provided correctly."}
    )

# Add a global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the exception internally
    print(f"Unexpected error: {str(exc)}")
    
    # Return a generic error response
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected error occurred. Please try again later."}
    )

