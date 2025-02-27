import os
from fastapi import FastAPI
from api.endpoints import router as api_router  # Correct import for the main router
import uvicorn

app = FastAPI()

# Include the endpoints from api.endpoints
app.include_router(api_router)

# Get the port from environment variables, or default to 7454
port = int(os.getenv("PORT", 7454))  # Use environment variable or default to 7454

if __name__ == "__main__":
    # Pass the app as a string to uvicorn.run
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)  # 'main:app' is the import string for the app
